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
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
        "sales": [100, 150, 200, 130, 170],
        "category": ["A", "B", "A", "B", "A"]
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
    discovery_state = {
        "sql_result": {"rows": [("2023-01-01", 100), ("2023-01-02", 150)], "columns": ["date", "sales"]},
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
    query = "Show me sales over time and forecast next values."
    
    print(f"Running query: {query}")
    result = orchestrator.run(query)
    
    # 4. Check Results
    print("\n--- Checking Results ---")
    
    # SQL
    sql = result.get("sql_agent", {}).get("sql")
    print(f"SQL Generated: {sql}")
    if not sql:
        print("❌ SQL generation failed")
    else:
        print("✅ SQL generation success")

    # SQL Execution
    rows = result.get("sql_result", {}).get("rows")
    print(f"Rows returned: {len(rows) if rows else 0}")
    if not rows:
        print("❌ SQL execution failed or empty")
    else:
        print("✅ SQL execution success")

    # Charts
    charts = result.get("chart_agent", {}).get("charts", [])
    print(f"Charts generated: {len(charts)}")
    if not charts:
        print("⚠️ No charts generated (might be valid if LLM decided so)")
    else:
        print("✅ Charts generated")

    # Insights
    insights = result.get("insight_agent", {}).get("insights")
    if not insights:
        print("❌ Insights failed")
    else:
        print("✅ Insights generated")

    # Forecast
    forecast = result.get("forecast_agent", {}).get("forecast_text")
    if not forecast:
        print("❌ Forecast failed")
    else:
        print("✅ Forecast generated")

    # Report
    report = result.get("report_file")
    if report and os.path.exists(report):
        print(f"✅ Report generated at: {report}")
    else:
        print("❌ Report generation failed")

    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_pipeline()
