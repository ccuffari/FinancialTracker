# db_structure_generator/core.py
from .excel_reader import read_workbook
from .schema_infer import infer_column_properties
from .sql_builder import build_create_table_sql
from .rules import load_config
from pathlib import Path
import json

def generate_sql_from_excel(excel_path: str, config_path: str, out_dir: str):
    cfg = load_config(config_path)
    sheets = read_workbook(excel_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []
    for sheet_name, meta in sheets.items():
        headers = meta["headers"]
        columns = meta["columns"]
        inferred = infer_column_properties(sheet_name, headers, columns)
        # add first_formula_example into inferred metadata for comments
        for col in headers:
            inferred[col]["first_formula_example"] = meta["first_formula_example"].get(col)
        sql = build_create_table_sql(sheet_name, inferred, cfg)
        fname = out_dir / f"{sheet_name.lower().replace(' ','_')}.sql"
        fname.write_text(sql)
        generated_files.append(str(fname))
    # optionally dump metadata
    (out_dir / "metadata.json").write_text(json.dumps({k: {"headers": v["headers"], "has_formula": v["has_formula"]} for k,v in sheets.items()}, indent=2, default=str))
    return generated_files
