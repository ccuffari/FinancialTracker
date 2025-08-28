"""
Excel extractor: reads all sheets, filters by schema.table naming,
returns a mapping of { schema: { table: dataframe } }.
"""

import pandas as pd
import logging
import re
from typing import Dict
from utils import sanitize_identifier

logger = logging.getLogger(__name__)

SHEET_PATTERN = re.compile(r'^([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)$')

def extract_sheets(excel_path: str):
    """
    Read all sheets from excel_path and return a dict:
    { (schema, table): dataframe }
    Ignores sheets named public.overview or sheets not matching pattern.
    """
    logger.info("Reading Excel file: %s", excel_path)
    all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    out = {}
    for sheet_name, df in all_sheets.items():
        if sheet_name.lower() == "public.overview":
            logger.debug("Skipping public.overview sheet: %s", sheet_name)
            continue
        m = SHEET_PATTERN.match(sheet_name.strip())
        if not m:
            logger.info("Skipping sheet (not schema.table): %s", sheet_name)
            continue
        schema = sanitize_identifier(m.group(1))
        table = sanitize_identifier(m.group(2))
        # Ensure headers are strings and strip whitespace
        df.columns = [str(c).strip() for c in df.columns]
        out[(schema, table)] = df
        logger.info("Extracted sheet -> schema=%s table=%s rows=%d", schema, table, len(df))
    return out
