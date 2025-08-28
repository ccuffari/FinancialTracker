"""
Database utilities: connection and execution helpers.
"""

import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
import logging
from config import PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGPORT

logger = logging.getLogger(__name__)

def get_connection():
    """
    Return a new psycopg2 connection.
    """
    conn = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
        port=PGPORT
    )
    conn.autocommit = True
    return conn

def exec_statements(statements):
    """
    Execute a list of SQL (psycopg2.sql.SQL or strings).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for st in statements:
                logger.debug("Executing SQL: %s", st.as_string(cur) if hasattr(st, 'as_string') else st)
                if hasattr(st, 'as_string'):
                    cur.execute(st)
                else:
                    cur.execute(st)
    finally:
        conn.close()

def upsert_dates(date_list):
    """
    Insert dates into dates.dates if they don't exist and return mapping {date_iso: date_id}.
    date_list: iterable of datetime.date
    """
    conn = get_connection()
    mapping = {}
    try:
        with conn.cursor() as cur:
            # ensure table exists
            cur.execute("CREATE SCHEMA IF NOT EXISTS dates;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dates.dates (
                    date_id SERIAL PRIMARY KEY,
                    date DATE UNIQUE
                );
            """)
            # insert unique dates using ON CONFLICT DO NOTHING
            rows = [(d.isoformat(),) for d in set(d for d in date_list if d is not None)]
            if rows:
                insert_sql = "INSERT INTO dates.dates (date) VALUES %s ON CONFLICT (date) DO NOTHING"
                execute_values(cur, insert_sql, rows)
            # fetch ids
            cur.execute("SELECT date, date_id FROM dates.dates WHERE date IN %s;", (tuple(d.isoformat() for d in set(d for d in date_list if d is not None)),))
            for r in cur.fetchall():
                mapping[r[0]] = r[1]
    finally:
        conn.close()
    return mapping

def bulk_insert(schema, table, columns, rows, page_size=1000):
    """
    Bulk insert rows (iterable of tuples) into schema.table using execute_values.
    columns: list of column names
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            identifiers = [sql.Identifier(c) for c in columns]
            target = sql.Identifier(schema), sql.Identifier(table)
            cols_sql = sql.SQL(", ").join([sql.Identifier(c) for c in columns])
            insert_prefix = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(target[0], target[1], cols_sql)
            # chunked insert
            execute_values(cur, insert_prefix.as_string(cur), rows, page_size=page_size)
            logger.info("Inserted %d rows into %s.%s", len(rows), schema, table)
    finally:
        conn.close()
