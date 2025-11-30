import sqlite3
from pathlib import Path
from config.settings import DB_PATH


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Creates a safe SQLite connection with WAL mode + thread support.
    Optimized for multi-agent parallel reads.
    """

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False   # <--- IMPORTANT for multithreading
    )

    conn.row_factory = sqlite3.Row  # return rows as dict-like

    # Optimize SQLite for parallel workloads
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")

    return conn