import os
from pathlib import Path

# -----------------------------------------------------
# BASE DIRECTORIES
# -----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
TOOLS_DIR = BASE_DIR / "tools"
AGENTS_DIR = BASE_DIR / "agents"
UI_DIR = BASE_DIR / "ui"
ORCHESTRATOR_DIR = BASE_DIR / "orchestrator"

# -----------------------------------------------------
# DATA FILES
# -----------------------------------------------------
RAW_DATA_PATH = DATA_DIR / "uploaded_raw.csv"       # file uploaded by UI
CLEAN_DATA_PATH = DATA_DIR / "clean_data.csv"       # after cleaning

# -----------------------------------------------------
# DATABASE CONFIG
# -----------------------------------------------------
DB_PATH = DB_DIR / "data.db"                        # SQLite DB
DEFAULT_TABLE_NAME = "uploaded_table"

# Schema file generated after DB load
SCHEMA_PATH = DB_DIR / "schema.json"

# -----------------------------------------------------
# REPORT STORAGE
# -----------------------------------------------------
REPORTS_DIR = ORCHESTRATOR_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# UI / TEMP STORAGE
# -----------------------------------------------------
ASSETS_DIR = UI_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# LOGS (optional)
# -----------------------------------------------------
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# GENERAL APP SETTINGS
# -----------------------------------------------------
MAX_PREVIEW_ROWS = 50
MAX_SQL_ROWS = 5000

# Ensure core directories exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)