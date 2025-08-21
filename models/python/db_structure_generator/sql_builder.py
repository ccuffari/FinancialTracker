# db_structure_generator/sql_builder.py
from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime

def build_create_table_sql(sheet_name: str, columns_meta: Dict[str, Dict], config: Dict) -> str:
    """
    Costruisce un CREATE TABLE SQL idempotente con:
    - PK sulla colonna 'date' (tranne per sheet 'dates')
    - per colonne derived aggiunge COMMENT ON COLUMN con formula hint
    - FK per date -> dates.date (dates.date deve essere UNIQUE)
    """
    schema = config.get("schema", "public")
    table_name = config.get("table_name_prefix","") + sheet_name.lower().replace(" ", "_")
    lines = []
    pk_clause = ""
    cols_sql = []
    for col, meta in columns_meta.items():
        col_esc = f'"{col}"' if not col.isidentifier() else col
        sql_type = meta["sql_type"]
        nullable = meta["nullable"]
        null_str = "" if not nullable else " NULL"
        cols_sql.append(f"  {col_esc} {sql_type}{null_str}")
    # PK / FK logic:
    if sheet_name.lower() == "dates":
        # dates: expect id + date, make id primary key and date unique
        if "id" not in columns_meta:
            # if id missing, create id serial
            cols_sql.insert(0, "  id SERIAL NOT NULL")
        pk_clause = "PRIMARY KEY (id)"
        unique_date = True if "date" in columns_meta else False
    else:
        # other sheets: 'date' is primary key and foreign key to dates(date)
        if "date" not in columns_meta:
            raise ValueError(f"Sheet {sheet_name} expected 'date' column")
        pk_clause = f"PRIMARY KEY (date)"
        # ensure FK will reference dates(date)
    # combine
    table_body = ",\n".join(cols_sql)
    if pk_clause:
        table_body += ",\n  " + pk_clause
    create_sql = f'CREATE TABLE IF NOT EXISTS "{schema}"."{table_name}" (\n{table_body}\n);\n'
    # additional constraints
    extras = []
    if sheet_name.lower() == "dates" and "date" in columns_meta:
        extras.append(f'-- ensure dates.date is unique for FK references\nCREATE UNIQUE INDEX IF NOT EXISTS ux_{table_name}_date ON "{schema}"."{table_name}" ("date");\n')
    elif sheet_name.lower() != "dates":
        # add FK referencing dates.date
        extras.append(f'ALTER TABLE IF EXISTS "{schema}"."{table_name}" ADD CONSTRAINT fk_{table_name}_date FOREIGN KEY ("date") REFERENCES "{schema}"."dates" ("date");\n')
    # add comments for derived columns
    comments = []
    for col, meta in columns_meta.items():
        if meta.get("derived"):
            example = meta.get("first_formula_example") or ""
            comment = f"derived column (formula example: {example})"
            col_esc = f'"{col}"' if not col.isidentifier() else col
            comments.append(f"COMMENT ON COLUMN \"{schema}\".\"{table_name}\".{col_esc} IS '{comment}';\n")
    return create_sql + "\n".join(extras) + "\n".join(comments)
