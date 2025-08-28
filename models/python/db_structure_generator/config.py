"""
Configuration module: database settings and file locations.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # read from .env if present

PGHOST = os.getenv("PGHOST", "ep-cold-wave-a9ixok7s-pooler.gwc.azure.neon.tech")
PGDATABASE = os.getenv("PGDATABASE", "neondb")
PGUSER = os.getenv("PGUSER", "neondb_owner")
PGPASSWORD = os.getenv("PGPASSWORD", "npg_q2vBgXHbn1ix")
PGPORT = int(os.getenv("PGPORT", 5432))

EXCEL_FILE = os.getenv("EXCEL_FILE", "../data/financialTracker.xlsx")
LOG_FILE = os.getenv("LOG_FILE", "logs/financial_etl.log")
