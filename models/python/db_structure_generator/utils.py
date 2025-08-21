# db_structure_generator/utils.py
from datetime import datetime

def parse_mm_yyyy_to_date(s: str):
    """
    "MM/YYYY" -> datetime.date (first day of month)
    If s already date/datetime, return date.
    """
    if s is None:
        return None
    if isinstance(s, (datetime, )):
        return s.date()
    s = str(s).strip()
    # allow formats like "01/2023" or "1/2023" or "01-2023"
    try:
        parts = s.replace("-", "/").split("/")
        if len(parts) >= 2:
            mm = int(parts[0])
            yyyy = int(parts[1])
            return datetime(year=yyyy, month=mm, day=1).date()
    except Exception:
        pass
    # fallback: try dateutil
    try:
        from dateutil import parser
        d = parser.parse(s, dayfirst=True)
        return d.date()
    except Exception:
        return None
