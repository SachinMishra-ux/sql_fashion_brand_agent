"""
db.py
Compatibility wrapper re-exporting MySQL database helpers from mysql_db.py.
"""
from mysql_db import (
    DB_CONFIG,
    get_connection,
    check_connection,
    get_schema,
    run_query,
)

__all__ = [
    "DB_CONFIG",
    "get_connection",
    "check_connection",
    "get_schema",
    "run_query",
]
