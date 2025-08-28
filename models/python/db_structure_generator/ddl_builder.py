"""
DDL builder: produce SQL commands for creating schemas and tables.
Handles special date formats like 'September-25' by mapping them to DATE
(via the dates.dates table, which keeps normalized DATE values).
"""

from psycopg2 import sql
import logging
from utils import infer_column_type, sanitize_identifier

logger = logging.getLogger(__name__)

def build_create_schema(schema_name: str):
    """
    Return SQL (psycopg2.sql.SQL) to create schema if not exists.
    """
    return sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name))

def build_create_dates_table():
    """
    Return SQL to create dates.dates table.
    Central dimension for date values.
    """
    return sql.SQL("""
    CREATE SCHEMA IF NOT EXISTS dates;
    CREATE TABLE IF NOT EXISTS dates.dates (
        date_id SERIAL PRIMARY KEY,
        date DATE UNIQUE
    );
    """)

def build_create_table(schema: str, table: str, df_columns):
    """
    Build CREATE TABLE SQL for schema.table given df_columns (list of column names).
    Column typing rules:
     - INTEGER => INTEGER
     - DATE => handled with FK to dates.dates
     - STRING => VARCHAR(50) (default max length)
     - else => DECIMAL(18,4)
    """
    schema_s = sanitize_identifier(schema)
    table_s = sanitize_identifier(table)

    col_defs = []
    fk_defs = []

    for col in df_columns:
        col_safe = sanitize_identifier(col)
        col_type = infer_column_type(col)

        if col_type == "INTEGER":
            if col.lower() == "id":
                col_defs.append(sql.SQL("{} INTEGER PRIMARY KEY").format(sql.Identifier(col_safe)))
            else:
                col_defs.append(sql.SQL("{} INTEGER").format(sql.Identifier(col_safe)))

        elif col_type == "DATE":
            if schema_s == "dates" and table_s == "dates":
                # nella tabella centrale delle date manteniamo DATE
                col_defs.append(sql.SQL("{} DATE").format(sql.Identifier(col_safe)))
            else:
                # altrove usiamo FK alla tabella dates
                col_defs.append(sql.SQL("{} INTEGER").format(sql.Identifier(col_safe)))
                fk_name = f"{table_s}_{col_safe}_dates_fk"
                fk_stmt = sql.SQL(
                    "ALTER TABLE {}.{} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES dates.dates(date_id);"
                ).format(
                    sql.Identifier(schema_s),
                    sql.Identifier(table_s),
                    sql.Identifier(fk_name),
                    sql.Identifier(col_safe)
                )
                fk_defs.append(fk_stmt)

        elif col_type == "STRING":
            # sempre VARCHAR(50) per default
            col_defs.append(sql.SQL("{} VARCHAR(50)").format(sql.Identifier(col_safe)))

        else:
            col_defs.append(sql.SQL("{} DECIMAL(18,4)").format(sql.Identifier(col_safe)))

    create_tbl = sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ( {} );").format(
        sql.Identifier(schema_s),
        sql.Identifier(table_s),
        sql.SQL(", ").join(col_defs) if col_defs else sql.SQL("")
    )

    # prima CREATE TABLE, poi le ALTER TABLE con FK
    return [create_tbl] + fk_defs
