"""
Main orchestrator script.

Usage:
    python main.py

It will:
 - read excel file
 - build schemas and create tables
 - run ETL to insert rows
"""

import logging
import os
from config import EXCEL_FILE, LOG_FILE
from extractor import extract_sheets
from ddl_builder import build_create_schema, build_create_dates_table, build_create_table
from db import exec_statements
from etl import load_dataframe_to_table
from psycopg2 import sql

# logging setup
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
)
logger = logging.getLogger("financial_etl")

def build_create_dates_table_from_columns(schema, table, columns, pk_col=None, date_col=None):
    """
    Build CREATE TABLE statement for dates table using provided columns.
    
    Args:
        schema: Schema name
        table: Table name  
        columns: List of column names from the dataframe
        pk_col: Primary key column name (if None, will use 'date_id')
        date_col: Date column name (if None, will use 'date')
    
    Returns:
        List of SQL statements
    """
    if pk_col is None:
        pk_col = "date_id"
    if date_col is None:
        date_col = "date"
    
    # Start building the CREATE TABLE statement
    stmt_parts = [f"CREATE TABLE IF NOT EXISTS {schema}.{table} ("]
    
    column_defs = []
    
    # Add primary key column
    if pk_col in columns:
        column_defs.append(f"    {pk_col} SERIAL PRIMARY KEY")
    else:
        # If pk_col not in original columns, add it as SERIAL
        column_defs.append(f"    {pk_col} SERIAL PRIMARY KEY")
    
    # Add other columns
    for col in columns:
        if col != pk_col:  # Skip pk column as it's already added
            if col == date_col or 'date' in col.lower():
                column_defs.append(f"    {col} DATE")
            else:
                column_defs.append(f"    {col} TEXT")
    
    stmt_parts.append(",\n".join(column_defs))
    stmt_parts.append(");")
    
    return ["\n".join(stmt_parts)]

def main():
    logger.info("Starting financial ETL")
    # main.py — snippet (replace the part after mapping = extract_sheets(...))

    mapping = extract_sheets(EXCEL_FILE)  # {(schema,table): df}

    # Handle special case: if Excel contains dates.dates sheet, use its columns/names
    dates_df = None
    dates_schema = "dates"
    dates_table = "dates"
    dates_pk_col = None        # name of pk column in dates table (e.g., 'id' or 'date_id')
    dates_date_col = None      # name of the column that stores the date value (e.g., 'date')

    if (dates_schema, dates_table) in mapping:
        dates_df = mapping.pop((dates_schema, dates_table))
        # detect pk column (prefer any column whose name contains 'id' or endswith '_id')
        cols_lower = [c.lower() for c in dates_df.columns]
        for c in dates_df.columns:
            if c.lower() == "id" or c.lower().endswith("_id"):
                dates_pk_col = c
                break
        # detect the column that is date-like
        for c in dates_df.columns:
            if "date" in c.lower():
                dates_date_col = c
                break
        # If no pk found, we will create one named date_id (but user prefers keeping names,
        # so we only do this if absolutely necessary)
        if dates_pk_col is None:
            dates_pk_col = "date_id"
            # ensure it's added to DDL as SERIAL even if not present in df

    # create schemas
    schemas = set([s for s, t in mapping.keys()])
    statements = []
    for s in schemas:
        statements.append(build_create_schema(s))
    # ensure dates schema exists
    statements.append(build_create_schema(dates_schema))

    try:
        exec_statements(statements)
    except Exception as e:
        logger.exception("Error creating schemas: %s", e)
        raise

    # create dates.dates table (respecting Excel column names if provided)
    try:
        if dates_df is not None:
            stmts = build_create_dates_table_from_columns(dates_schema, dates_table, list(dates_df.columns), pk_col=dates_pk_col, date_col=dates_date_col)
            exec_statements(stmts)
        else:
            exec_statements([build_create_dates_table()])  # fallback legacy
    except Exception as e:
        logger.exception("Error creating dates table: %s", e)
        raise

    # create each table DDL using the actual pk name of dates table for FK references
    for (schema, table), df in mapping.items():
        try:
            stmts = build_create_table(schema, table, list(df.columns), dates_pk_col=dates_pk_col)
            exec_statements(stmts)
            logger.info("Created/ensured table %s.%s", schema, table)
        except Exception as e:
            logger.exception("Error creating table %s.%s: %s", schema, table, e)
            raise

    # run ETL for each table (skip dates.dates, which is managed specially)
    for (schema, table), df in mapping.items():
        try:
            logger.info("Loading data for %s.%s (%d rows)", schema, table, len(df))
            load_dataframe_to_table(schema, table, df, dates_pk_col=dates_pk_col, dates_date_col=dates_date_col)
            logger.info("Loaded data for %s.%s", schema, table)
        except Exception as e:
            logger.exception("ETL error for %s.%s: %s", schema, table, e)
            raise

if __name__ == "__main__":
    main()