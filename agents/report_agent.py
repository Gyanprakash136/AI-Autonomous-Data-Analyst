from agents.base_agent import BaseAgent
from tools.pdf_tool import generate_pdf_report

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReportAgent")

    def run(self, shared_state: dict) -> dict:
        """
        Generates the PDF report using the full session history.
        """
        # Extract history passed from Orchestrator
        history = shared_state.get("history", [])
        
        # Create a snapshot of the current turn
        current_turn = {
            "user_query": shared_state.get("user_query", ""),
            "insight_agent": shared_state.get("insight_agent", {}),
            "forecast_agent": shared_state.get("forecast_agent", {}),
            "chart_agent": shared_state.get("chart_agent", {})
        }
        
        # Combine history + current
        full_history = history + [current_turn]
        
        pdf_path = generate_pdf_report(full_history)
        
        if pdf_path:
            print(f"[ReportAgent] PDF generated at: {pdf_path}")
            shared_state["report_file"] = pdf_path
        else:
            print("[ReportAgent] PDF generation failed.")
            shared_state["report_file"] = None
            
        return shared_state