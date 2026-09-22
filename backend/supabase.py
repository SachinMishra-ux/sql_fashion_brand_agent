"""
supabase.py
Handles Supabase / PostgreSQL database connectivity, health checks,
and LangGraph checkpointer initialization (PostgresSaver).
"""
import logging
import os
import re
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv(override=True)

logger = logging.getLogger(__name__)


def get_postgres_connection_info() -> str | None:
    """
    Parses PostgreSQL connection details from environment variables.
    Handles special characters in passwords cleanly and supports
    direct or pooler connection strings.
    """
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER")
    dbname = os.getenv("POSTGRES_DB", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")

    raw_conn_str = os.getenv("POSTGRES_CONN_STR", "").strip().strip('"').strip("'")

    if not password and raw_conn_str:
        # Extract user, password, host, port, dbname from connection string
        match = re.match(r"^postgresql://([^:]+):(.*)@([^@/:]+)(?::(\d+))?/(.+)$", raw_conn_str)
        if match:
            user = user or match.group(1)
            password = match.group(2)
            host = host or match.group(3)
            port = port or match.group(4) or "5432"
            dbname = dbname or match.group(5)

    if host and user and password:
        return f"host={host} port={port} dbname={dbname} user={user} password={password}"
    elif raw_conn_str:
        return raw_conn_str
    return None


def check_postgres_connection() -> dict:
    """
    Checks connection to Supabase / PostgreSQL database.
    Raises an exception if connection fails.
    """
    conn_info = get_postgres_connection_info()
    if not conn_info:
        raise ValueError("PostgreSQL/Supabase connection details are not configured in environment.")

    import psycopg

    with psycopg.connect(conn_info, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()

    return {"status": "ok", "service": "supabase"}


def init_checkpointer():
    """
    Initializes PostgreSQL checkpointer using PostgresSaver with connection pool.
    Falls back to MemorySaver if the PostgreSQL instance is unreachable.
    """
    conn_info = get_postgres_connection_info()
    if conn_info:
        pool = None
        try:

            # Quick probe to verify host reachability before initializing pool
            with psycopg.connect(conn_info, connect_timeout=3) as _:
                pass

            pool = ConnectionPool(
                conninfo=conn_info,
                max_size=10,
                kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
            )

            checkpointer = PostgresSaver(pool)
            checkpointer.setup()
            logger.info("Successfully initialized PostgreSQL PostgresSaver checkpointer.")
            return checkpointer
        except Exception as e:
            if pool is not None:
                try:
                    pool.close()
                except Exception:
                    pass
            logger.warning(
                f"Unable to connect to PostgreSQL checkpointer ({e}). "
                "Falling back to MemorySaver for session state persistence."
            )

    return MemorySaver()


# Global checkpointer instance
_checkpointer = None


def get_checkpointer():
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = init_checkpointer()
    return _checkpointer
