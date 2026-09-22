import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


load_dotenv(override=True)

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql-34425d40-sachin19566-5236.g.aivencloud.com"),
    "port": int(os.getenv("MYSQL_PORT", "16512")),
    "user": os.getenv("MYSQL_USER", "avnadmin"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "defaultdb"),
    "ssl_disabled": False,
    "ssl_verify_cert": False,   # Aiven uses self-signed certs
    "connection_timeout": 10,
}


def get_connection():
    """Returns a new MySQL connection using Aiven credentials."""
    return mysql.connector.connect(**DB_CONFIG)


def get_schema() -> str:
    """
    Dynamically reads the CREATE TABLE SQL for all tables in the database.
    Used to inject schema context into the LLM's system prompt.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"SHOW CREATE TABLE `{table}`;")
        row = cursor.fetchone()
        if row:
            schema_parts.append(row[1])

    cursor.close()
    conn.close()
    return "\n\n".join(schema_parts)


def run_query(sql: str) -> list[dict]:
    """
    Executes a SQL SELECT query and returns results as a list of dicts.
    Raises an exception with the MySQL error message on failure.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
