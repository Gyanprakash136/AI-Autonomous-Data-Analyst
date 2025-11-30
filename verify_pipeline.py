import sys
import os
import pandas as pd
from orchestrator.root_orchestrator import RootOrchestrator
from tools.sql_tool import load_csv_to_db

from dotenv import load_dotenv

def verify_pipeline():
    load_dotenv()
    print("--- Starting Verification ---")
    
    # 1. Create dummy CSV
    csv_path = "test_data.csv"
    # Create 20 rows of data
    dates = pd.date_range(start="2023-01-01", periods=20).strftime("%Y-%m-%d").tolist()
    sales = [100 + i*10 for i in range(20)]
    categories = ["A", "B"] * 10
    
    df = pd.DataFrame({
        "date": dates,
        "sales": sales,
        "category": categories
    })
    df.to_csv(csv_path, index=False)
    print("Created test_data.csv")

    # 2. Load to DB
    print("Loading data to DB...")
    success = load_csv_to_db(csv_path)
    if not success:
        print("Failed to load data.")
        return

    # Initialize orchestrator for both discovery and main query
    orchestrator = RootOrchestrator()

    # 2. Test Discovery Mode
    print("Running Discovery Mode...")
    # Fetch data from DB to simulate UI behavior
    import sqlite3
    conn = sqlite3.connect('db/analyst.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data_table")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()
    
    discovery_state = {
        "sql_result": {"rows": rows, "columns": columns},
        "user_query": ""
    }
    discovery_result = orchestrator.run_discovery(discovery_state)
    
    # Check discovery results
    rec_questions = discovery_result.get("insight_agent", {}).get("recommended_questions", [])
    overview_charts = discovery_result.get("chart_agent", {}).get("charts", [])
    
    if rec_questions:
        print(f"✅ Discovery: Generated {len(rec_questions)} recommended questions.")
    else:
        print("❌ Discovery: No recommended questions.")
        
    if overview_charts:
        print(f"✅ Discovery: Generated {len(overview_charts)} overview charts.")
    else:
        print("❌ Discovery: No overview charts.")

    # 3. Run Pipeline (Query)
    # --- Pipeline Run 1 ---
    query1 = "Show me sales over time."
    print(f"Running query 1: {query1}")
    
    # Run pipeline
    result1 = orchestrator.run(query1, history=[])
    
    # Simulate saving to history
    history = [{
        "user_query": query1,
        "insight_agent": result1.get("insight_agent", {}),
        "forecast_agent": result1.get("forecast_agent", {}),
        "chart_agent": result1.get("chart_agent", {})
    }]
    
    # --- Pipeline Run 2 ---
    query2 = "What is the average sales?"
    print(f"Running query 2: {query2}")
    
    result2 = orchestrator.run(query2, history=history)
    
    print("--- Checking Results ---")
    
    # Check SQL
    sql = result2.get("sql_agent", {}).get("sql")
    print(f"SQL Generated: {sql}")
    if sql:
        print("✅ SQL generation success")
    else:
        print("❌ SQL generation failed")

    # Check SQL Execution
    rows = result2.get("sql_result", {}).get("rows")
    if rows:
        print(f"Rows returned: {len(rows)}")
        print("✅ SQL execution success")
    else:
        print("❌ SQL execution failed (or empty result)")

    # Check Charts
    charts = result2.get("chart_agent", {}).get("charts", [])
    print(f"Charts generated: {len(charts)}")
    if len(charts) > 0:
        print("✅ Charts generated")
    
    # Check Insights
    if result2.get("insight_agent", {}).get("insights"):
        print("✅ Insights generated")
        
    # Check Forecast
    if result2.get("forecast_agent", {}).get("forecast_text"):
        print("✅ Forecast generated")

    # Check Report
    report_path = result2.get("report_file")
    if report_path and os.path.exists(report_path):
        print(f"✅ Report generated at: {report_path}")
    else:
        print("❌ Report generation failed")

    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_pipeline()
