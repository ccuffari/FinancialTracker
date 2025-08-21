# db_structure_generator/rules.py
import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULTS = {
    "schema": "public",
    "monetary_type": "NUMERIC(18,2)",
    "table_name_prefix": "",
}

def load_config(path: str = None) -> Dict[str,Any]:
    cfg = DEFAULTS.copy()
    if path:
        p = Path(path)
        if p.exists():
            raw = yaml.safe_load(p.read_text())
            if raw:
                cfg.update(raw)
    return cfg
