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

def main():
    logger.info("Starting financial ETL")
    mapping = extract_sheets(EXCEL_FILE)  # {(schema,table): df}
    # collect schemas
    schemas = set([s for s, t in mapping.keys()])
    # create schema statements
    statements = []
    for s in schemas:
        statements.append(build_create_schema(s))
    # create dates.dates
    statements.append(sql.SQL("SELECT 1;"))  # placeholder (ensures list type)
    # execute schema creation
    try:
        exec_statements(statements)
        # create dates table
        exec_statements([build_create_dates_table()])
    except Exception as e:
        logger.exception("Error creating schemas/dates table: %s", e)
        raise

    # create each table DDL
    for (schema, table), df in mapping.items():
        try:
            stmts = build_create_table(schema, table, list(df.columns))
            exec_statements(stmts)
            logger.info("Created/ensured table %s.%s", schema, table)
        except Exception as e:
            logger.exception("Error creating table %s.%s: %s", schema, table, e)
            raise

    # run ETL for each table
    for (schema, table), df in mapping.items():
        try:
            logger.info("Loading data for %s.%s (%d rows)", schema, table, len(df))
            load_dataframe_to_table(schema, table, df)
            logger.info("Loaded data for %s.%s", schema, table)
        except Exception as e:
            logger.exception("ETL error for %s.%s: %s", schema, table, e)
            raise

    logger.info("ETL finished successfully")

if __name__ == "__main__":
    main()
