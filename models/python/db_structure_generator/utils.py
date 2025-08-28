"""
Utility helpers: sanitization, inference, parsing.
"""

import re
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

NAME_SAFE_RE = re.compile(r'^[A-Za-z0-9_]+$')

def sanitize_identifier(name: str) -> str:
    """
    Return a sanitized DB identifier (letters, digits, underscore).
    Non matching characters are replaced by underscore.
    """
    if not name:
        return name
    cleaned = re.sub(r'[^A-Za-z0-9_]', '_', name)
    # avoid starting with digit
    if re.match(r'^[0-9]', cleaned):
        cleaned = "_" + cleaned
    return cleaned

def infer_column_type(col_name: str, sample_values=None) -> str:
    """
    Infer column type from header name and sample values.
    """
    name = col_name.lower()
    if name == "id" or name.endswith("_id") or name == "identifier":
        return "INTEGER"
    if "id" == name or name.lower().endswith("id"):
        return "INTEGER"
    if "date" in name:
        return "DATE"
    
    # fallback: controlla se i valori sembrano numerici
    if sample_values:
        from decimal import Decimal
        numeric_count = 0
        total = 0
        for v in sample_values:
            total += 1
            try:
                Decimal(str(v))
                numeric_count += 1
            except Exception:
                pass
        # se la maggior parte sono numerici → DECIMAL
        if total > 0 and numeric_count / total > 0.7:
            return "DECIMAL"
    
    # altrimenti → STRING
    return "STRING"


def parse_date_mm_yyyy(value):
    """
    Parse date strings in formats like "MM/YYYY" or "M/YYYY" or "MM-YYYY" and return a datetime.date.
    Returns None if not parsable.
    """
    if value is None:
        return None
    if isinstance(value, (datetime, )):
        return value.date()
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return None
    # Accept formats: MM/YYYY, M/YYYY, MM-YYYY, YYYY-MM, YYYY/MM, etc.
    # try common patterns
    try:
        # try parsing directly with dateutil via many formats
        from dateutil import parser
        dt = parser.parse(s, dayfirst=False, fuzzy=True, default=datetime(1900,1,1))
        return dt.date()
    except Exception:
        # fallback manual MM/YYYY
        m = re.match(r'^\s*(\d{1,2})\D+(\d{4})\s*$', s)
        if m:
            mm = int(m.group(1))
            yyyy = int(m.group(2))
            try:
                return datetime(yyyy, mm, 1).date()
            except Exception:
                return None
    return None

def normalize_decimal(value):
    """
    Normalize numeric strings like '12.345,67 €' or '12345.67' to Decimal('12345.67').
    If value already numeric return Decimal.
    Returns None if empty or not parseable.
    """
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except Exception:
            return None
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return None
    # remove euro symbol and whitespace
    s = s.replace('€', '').replace(' ', '')
    # If contains comma as decimal separator and dot as thousands: "12.345,67"
    if s.count(',') == 1 and s.count('.') > 0:
        s = s.replace('.', '').replace(',', '.')
    # If contains comma only: "12345,67"
    elif s.count(',') == 1 and s.count('.') == 0:
        s = s.replace(',', '.')
    # remove any remaining non-digit/.- chars
    s = re.sub(r'[^\d\.\-]', '', s)
    try:
        return Decimal(s)
    except Exception:
        logger.debug("Could not parse decimal from %r", value)
        return None

