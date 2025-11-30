import json
import pandas as pd
from pathlib import Path

from config.settings import (
    CLEAN_DATA_PATH,
    DB_PATH,
    DEFAULT_TABLE_NAME,
    SCHEMA_PATH
)
from db.connection import get_connection


# ---------------------------------------------------------
# 1. CLEAN CSV
# ---------------------------------------------------------
def clean_csv(input_path: Path, output_path: Path) -> pd.DataFrame:
    """
    Clean CSV:
    - remove empty rows
    - normalize column names
    - dedupe duplicate columns
    - convert dtypes
    """

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = pd.read_csv(input_path)

    # Drop empty rows
    df = df.dropna(how="all")

    if df.empty:
        raise ValueError("Uploaded CSV has no valid rows.")

    # Normalize column names
    def normalize_col(c: str) -> str:
        return (
            c.strip()
             .replace(" ", "_")
             .replace("-", "_")
             .replace("/", "_")
             .replace(".", "_")
             .lower()
        )

    df.columns = [normalize_col(c) for c in df.columns]

    # Dedupe duplicated column names
    seen = {}
    new_cols = []
    for col in df.columns:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    df.columns = new_cols

    # Convert data types automatically
    df = df.convert_dtypes()

    # Save cleaned CSV
    df.to_csv(output_path, index=False)

    return df


# ---------------------------------------------------------
# 2. LOAD CLEAN CSV → SQLITE
# ---------------------------------------------------------
def load_csv_to_db(
    csv_path: Path = CLEAN_DATA_PATH,
    db_path: Path = DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME
) -> None:
    """
    Load cleaned CSV into SQLite using chunks for speed.
    """

    df = pd.read_csv(csv_path)

    conn = get_connection(db_path)
    try:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
            chunksize=10000,
            method="multi"
        )
    finally:
        conn.close()


# ---------------------------------------------------------
# 3. GENERATE SCHEMA.JSON
# ---------------------------------------------------------
def generate_schema_json(
    db_path: Path = DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
    schema_path: Path = SCHEMA_PATH
) -> dict:

    conn = get_connection(db_path)
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
    finally:
        conn.close()

    schema = {
        "table_name": table_name,
        "columns": [
            {
                "name": col["name"],
                "type": col["type"] or "TEXT"   # Fix empty types
            }
            for col in columns
        ]
    }

    # Save JSON
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    return schema


# ---------------------------------------------------------
# 4. FULL INGESTION PIPELINE
# ---------------------------------------------------------
def init_pipeline_from_csv(
    input_csv_path: Path,
    table_name: str = DEFAULT_TABLE_NAME
) -> dict:
    """
    1. Clean CSV
    2. Load into SQLite
    3. Generate schema.json
    """

    print("[init_db] Cleaning CSV...")
    df = clean_csv(input_csv_path, CLEAN_DATA_PATH)

    print("[init_db] Loading into database...")
    load_csv_to_db(CLEAN_DATA_PATH, DB_PATH, table_name)

    print("[init_db] Generating schema.json...")
    schema = generate_schema_json(DB_PATH, table_name, SCHEMA_PATH)

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "schema": schema
    }