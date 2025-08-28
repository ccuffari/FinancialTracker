"""
ETL module: minimal transformations and load into Postgres.
"""

import logging
from typing import Dict, Tuple, List
from utils import infer_column_type, parse_date_mm_yyyy, normalize_decimal
from db import upsert_dates, bulk_insert
from psycopg2 import sql

logger = logging.getLogger(__name__)

def prepare_table_rows(df):
    """
    Given a pandas DataFrame, infer columns, and return:
      (columns_list, rows_list, date_values)
    - columns_list: list of column names (sanitized)
    - rows_list: list of tuples ready to insert (with date columns replaced by their ISO date strings for now)
    - date_values: list of parsed dates to be upserted into dates.dates
    """
    # avoid importing pandas at module scope to keep this file testable
    import pandas as pd
    cols = [str(c).strip() for c in df.columns]
    parsed_rows = []
    date_values = []
    for idx, r in df.iterrows():
        out = []
        for col in cols:
            val = r.get(col)
            ctype = infer_column_type(col)
            if ctype == "DATE":
                parsed = parse_date_mm_yyyy(val)
                if parsed is None:
                    out.append(None)
                else:
                    # store temporary iso string; will be converted to date_id later
                    out.append(parsed.isoformat())
                    date_values.append(parsed)
            elif ctype == "INTEGER":
                try:
                    if val is None or (isinstance(val, float) and pd.isna(val)):
                        out.append(None)
                    else:
                        out.append(int(val))
                except Exception:
                    # if not parseable, append None
                    out.append(None)
            else:
                dec = normalize_decimal(val)
                out.append(dec)
        parsed_rows.append(tuple(out))
    return cols, parsed_rows, date_values

def load_dataframe_to_table(schema: str, table: str, df, db_upsert_dates=True):
    """
    Load a single dataframe into the target table.
    Steps:
     - prepare rows and collect date values
     - upsert dates into dates.dates (if any) and get mapping date.iso -> date_id
     - replace date iso strings in rows with date_id
     - insert rows via bulk_insert
    """
    cols, rows, date_values = prepare_table_rows(df)
    # if no rows -> nothing to do
    if not rows:
        logger.info("No rows to load for %s.%s", schema, table)
        return

    # upsert dates and get mapping
    date_map = {}
    if date_values and db_upsert_dates:
        mapping = upsert_dates(date_values)  # returns { 'YYYY-MM-DD': id }
        date_map = mapping

    # build final rows replacing date iso strings with date_id
    final_rows = []
    from utils import infer_column_type
    for row in rows:
        new_row = []
        for col_name, value in zip(cols, row):
            if infer_column_type(col_name) == "DATE":
                if value is None:
                    new_row.append(None)
                else:
                    # value is iso date string
                    new_row.append(date_map.get(value))
            else:
                new_row.append(value)
        final_rows.append(tuple(new_row))

    # perform bulk insert
    # convert Decimal(None) -> None is OK; psycopg2 handles Decimal
    bulk_insert(schema, table, cols, final_rows)
