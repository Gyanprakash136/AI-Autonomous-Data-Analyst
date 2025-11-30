import streamlit as st
import sys
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure root import visibility
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.root_orchestrator import RootOrchestrator
from tools.sql_tool import load_csv_to_db

st.set_page_config(page_title="AI Data Analyst", layout="wide")

def main():
    st.title("🤖 AI Autonomous Data Analyst")
    st.markdown("---")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "discovery_data" not in st.session_state:
        st.session_state.discovery_data = None
    if "history" not in st.session_state:
        st.session_state.history = []

    # Sidebar for setup
    with st.sidebar:
        st.header("Setup")
        uploaded_file = st.file_uploader("Upload CSV Data", type=["csv"])
        
        if uploaded_file:
            if st.button("Load & Analyze Data"):
                with st.spinner("Loading and running initial discovery..."):
                    # Load to DB
                    success = load_csv_to_db(uploaded_file)
                    if success:
                        st.success("Data loaded!")
                        
                        # Run Discovery
                        orchestrator = RootOrchestrator()
                        # We need to pass the data to discovery, but currently it reads from DB.
                        # We can just pass a dummy state with sql_result populated from a "select * limit 5"
                        # Or better, let's just fetch a sample in the UI and pass it?
                        # Actually, let's make a helper to get sample data.
                        
                        import sqlite3
                        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '../db/analyst.db'))
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM data_table LIMIT 1000")
                        rows = cursor.fetchall()
                        columns = [description[0] for description in cursor.description]
                        conn.close()
                        
                        discovery_state = {
                            "sql_result": {"rows": rows, "columns": columns},
                            "user_query": "" # No query for discovery
                        }
                        
                        result = orchestrator.run_discovery(discovery_state)
                        st.session_state.discovery_data = result
                    else:
                        st.error("Failed to load data.")

    # Main Area
    
    # 1. Discovery Section (Charts & Recommendations)
    if st.session_state.discovery_data:
        st.subheader("🚀 Data Overview")
        
        # Charts
        charts = st.session_state.discovery_data.get("chart_agent", {}).get("charts", [])
        if charts:
            cols = st.columns(len(charts))
            for i, chart in enumerate(charts):
                with cols[i]:
                    st.caption(chart.get("spec", {}).get("title", "Overview Chart"))
                    img_data = chart.get("png")
                    if img_data:
                        st.image(base64.b64decode(img_data))
        
        # Recommendations
        st.subheader("💡 Recommended Questions")
        questions = st.session_state.discovery_data.get("insight_agent", {}).get("recommended_questions", [])
        
        cols = st.columns(3)
        for i, q in enumerate(questions):
            if cols[i % 3].button(q, key=f"rec_{i}"):
                # Set as user query
                st.session_state.user_query_input = q

    # 2. Chat Interface
    user_query = st.text_input("Ask a question about your data:", key="user_query_input", placeholder="e.g., Show me sales trends over time")

    if st.button("Analyze Query") and user_query:
        orchestrator = RootOrchestrator()
        
        with st.spinner("Running AI Analysis Pipeline..."):
            try:
                # Pass history to orchestrator
                result = orchestrator.run(user_query, history=st.session_state.history)
                
                # Append result to history for next time
                # We only need specific fields to save space/context
                history_item = {
                    "user_query": user_query,
                    "insight_agent": result.get("insight_agent", {}),
                    "forecast_agent": result.get("forecast_agent", {}),
                    "chart_agent": result.get("chart_agent", {})
                }
                st.session_state.history.append(history_item)
                
                # 1. SQL Results
                st.subheader("📊 Data Query")
                sql_result = result.get("sql_result", {})
                if sql_result.get("error"):
                    st.error(f"SQL Error: {sql_result['error']}")
                else:
                    st.code(result.get("sql_agent", {}).get("sql", "No SQL generated"), language="sql")
                    rows = sql_result.get("rows", [])
                    cols = sql_result.get("columns", [])
                    if rows:
                        st.dataframe([dict(zip(cols, row)) for row in rows])
                    else:
                        st.warning("No data returned from query.")

                # 2. Insights & Forecast
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💡 Insights")
                    insights = result.get("insight_agent", {}).get("insights", "No insights available.")
                    st.write(insights)

                with col2:
                    st.subheader("📈 Forecast")
                    forecast = result.get("forecast_agent", {}).get("forecast_text", "No forecast available.")
                    st.write(forecast)

                # 3. Charts
                st.subheader("🎨 Visualizations")
                charts = result.get("chart_agent", {}).get("charts", [])
                if charts:
                    cols = st.columns(len(charts))
                    for i, chart in enumerate(charts):
                        with cols[i]:
                            st.caption(chart.get("spec", {}).get("title", "Chart"))
                            img_data = chart.get("png")
                            if img_data:
                                st.image(base64.b64decode(img_data))
                else:
                    st.info("No charts generated.")

                # 4. Report
                st.subheader("📄 Report")
                report_path = result.get("report_file")
                if report_path and os.path.exists(report_path):
                    with open(report_path, "rb") as f:
                        st.download_button(
                            label="Download PDF Report",
                            data=f,
                            file_name=os.path.basename(report_path),
                            mime="application/pdf"
                        )
                else:
                    st.warning("Report generation failed.")

            except Exception as e:
                st.error(f"Pipeline Critical Error: {e}")
                import traceback
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()