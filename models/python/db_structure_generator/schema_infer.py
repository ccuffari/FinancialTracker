# db_structure_generator/schema_infer.py
from typing import Dict, List, Tuple, Any
from dateutil import parser
from decimal import Decimal
from .utils import parse_mm_yyyy_to_date
import statistics

NUMERIC_SQL_TYPE = "NUMERIC(18,2)"  # default monetario

def infer_column_properties(sheet_name: str, headers: List[str], columns: Dict[str, List[Any]]) -> Dict[str, Dict]:
    """
    Restituisce per ogni colonna:
    {
      "col_name": {
         "nullable": True/False,
         "sql_type": "NUMERIC(18,2)" / "DATE" / "VARCHAR(n)",
         "derived": True/False,
         "sample_values": [...]
      }
    }
    """
    result = {}
    for col in headers:
        vals = columns[col]
        # detect null
        non_null_vals = [v for v in vals if v is not None and not (isinstance(v, dict) and "__formula__" in v)]
        nullable = any(v is None or (isinstance(v, str) and v.strip()=="") for v in vals)
        derived = any(isinstance(v, dict) and "__formula__" in v for v in vals)
        # heuristics:
        if col.lower() == "date":
            sql_type = "DATE"
            result[col] = {"nullable": False, "sql_type": sql_type, "derived": derived, "sample": non_null_vals[:5]}
            continue
        # Try numeric: if all non-null can be parsed as number (or decimal)
        is_numeric = True
        for v in non_null_vals[:200]:
            if isinstance(v, (int, float, Decimal)):
                continue
            if isinstance(v, str):
                s = v.strip().replace("€","").replace(",",".").replace(" ", "")
                try:
                    float(s)
                    continue
                except:
                    is_numeric = False
                    break
            else:
                is_numeric = False
                break
        if is_numeric and non_null_vals:
            sql_type = NUMERIC_SQL_TYPE
        else:
            # fallback: varchar with max length
            max_len = 0
            for v in non_null_vals:
                sl = str(v)
                if len(sl) > max_len:
                    max_len = len(sl)
            max_len = max(50, min(max_len, 1000))
            sql_type = f"VARCHAR({max_len})"
        result[col] = {"nullable": nullable, "sql_type": sql_type, "derived": derived, "sample": non_null_vals[:5]}
    return result
