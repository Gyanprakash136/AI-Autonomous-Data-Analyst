import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/analyst.db')

def run_sql_tool(shared_state: dict) -> dict:
    """
    Executes the SQL query found in shared_state['sql_agent']['sql']
    against the SQLite database.
    Updates shared_state['sql_result'] with columns and rows.
    """
    sql_query = shared_state.get("sql_agent", {}).get("sql", "")
    
    if not sql_query:
        print("[SQL Tool] No SQL query found.")
        shared_state["sql_result"] = {"columns": [], "rows": [], "error": "No SQL query provided"}
        return shared_state

    try:
        # Ensure DB directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"[SQL Tool] Executing: {sql_query}")
        cursor.execute(sql_query)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert rows to list of lists for JSON serialization if needed, 
        # but list of tuples is fine for internal use.
        # We'll stick to list of tuples as returned by fetchall.
        
        shared_state["sql_result"] = {
            "columns": columns,
            "rows": rows,
            "error": None
        }
        print(f"[SQL Tool] Success: {len(rows)} rows returned.")

    except Exception as e:
        print(f"[SQL Tool] Error: {e}")
        shared_state["sql_result"] = {
            "columns": [],
            "rows": [],
            "error": str(e)
        }

    return shared_state

def load_csv_to_db(csv_file):
    """
    Helper to load a CSV file into the SQLite DB as 'data_table'.
    """
    try:
        df = pd.read_csv(csv_file)
        
        # Ensure DB directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("data_table", conn, if_exists="replace", index=False)
        conn.close()
        print(f"[SQL Tool] Loaded {len(df)} rows into 'data_table'.")
        return True
    except Exception as e:
        print(f"[SQL Tool] CSV Load Failed: {e}")
        return False