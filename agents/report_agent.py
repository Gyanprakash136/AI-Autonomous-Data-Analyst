from agents.base_agent import BaseAgent
from tools.pdf_tool import generate_pdf_report

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReportAgent")

    def run(self, shared_state: dict) -> dict:
        """
        Generates the PDF report.
        """
        pdf_path = generate_pdf_report(shared_state)
        
        if pdf_path:
            print(f"[ReportAgent] PDF generated at: {pdf_path}")
            shared_state["report_file"] = pdf_path
        else:
            print("[ReportAgent] PDF generation failed.")
            shared_state["report_file"] = None
            
        return shared_state