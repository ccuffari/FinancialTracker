"""
DDL builder: produce SQL commands for creating schemas and tables.
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
     - columns inferred as 'INTEGER' => INTEGER
     - columns inferred as 'DATE' => INTEGER (foreign key to dates.dates(date_id)), except for dates.dates itself
     - else => DECIMAL
    Returns a list of psycopg2.sql.SQL statements (CREATE TABLE and optional ALTER TABLE ... ADD CONSTRAINT).
    """
    # sanitize names
    schema_s = sanitize_identifier(schema)
    table_s = sanitize_identifier(table)

    col_defs = []
    fk_defs = []

    for col in df_columns:
        col_safe = sanitize_identifier(col)
        col_type = infer_column_type(col)
        if col_type == "INTEGER":
            # assume primary key if name is "id"
            if col.lower() == "id":
                col_defs.append(sql.SQL("{} INTEGER PRIMARY KEY").format(sql.Identifier(col_safe)))
            else:
                col_defs.append(sql.SQL("{} INTEGER").format(sql.Identifier(col_safe)))
        elif col_type == "DATE":
            # store as INTEGER referencing dates.dates(date_id), except when the target table is dates.dates itself
            if schema_s == "dates" and table_s == "dates":
                # for the central dates table, keep proper types (DATE)
                col_defs.append(sql.SQL("{} DATE").format(sql.Identifier(col_safe)))
            else:
                col_defs.append(sql.SQL("{} INTEGER").format(sql.Identifier(col_safe)))
                # build a safe constraint name and append a proper ALTER TABLE statement
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
        else:
            # DECIMAL(18,4) to be safe
            col_defs.append(sql.SQL("{} DECIMAL(18,4)").format(sql.Identifier(col_safe)))

    create_tbl = sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ( {} );").format(
        sql.Identifier(schema_s),
        sql.Identifier(table_s),
        sql.SQL(", ").join(col_defs) if col_defs else sql.SQL("")
    )

    # combine: create table first, then alter statements for FKs
    statements = [create_tbl]
    for fk in fk_defs:
        statements.append(fk)
    return statements