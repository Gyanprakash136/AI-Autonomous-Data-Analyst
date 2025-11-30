from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import base64
import os
import uuid

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '../orchestrator/reports')

def generate_pdf_report(shared_state: dict) -> str:
    """
    Generates a PDF report containing insights, forecast, and charts.
    Returns the absolute path to the generated PDF.
    """
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "AI Data Analyst Report")
        
        y_position = height - 100
        
        # User Query
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Query:")
        c.setFont("Helvetica", 12)
        c.drawString(100, y_position, shared_state.get("user_query", "N/A"))
        y_position -= 30

        # Insights
        insights = shared_state.get("insight_agent", {}).get("insights", "No insights generated.")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Insights:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        
        # Simple text wrapping for insights
        text_object = c.beginText(50, y_position)
        text_object.setFont("Helvetica", 10)
        # Split by newlines first
        lines = insights.split('\n')
        for line in lines:
            # Very basic wrapping (approx 80 chars)
            while len(line) > 80:
                text_object.textLine(line[:80])
                line = line[80:]
            text_object.textLine(line)
        c.drawText(text_object)
        
        # Adjust y_position based on text length (approx)
        y_position = text_object.getY() - 30

        # Forecast
        forecast = shared_state.get("forecast_agent", {}).get("forecast_text", "No forecast generated.")
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Forecast:")
        y_position -= 20
        
        text_object = c.beginText(50, y_position)
        text_object.setFont("Helvetica", 10)
        lines = forecast.split('\n')
        for line in lines:
            while len(line) > 80:
                text_object.textLine(line[:80])
                line = line[80:]
            text_object.textLine(line)
        c.drawText(text_object)
        
        y_position = text_object.getY() - 30

        # Charts
        charts = shared_state.get("chart_agent", {}).get("charts", [])
        for i, chart in enumerate(charts):
            if y_position < 300: # Need space for chart
                c.showPage()
                y_position = height - 50
            
            c.setFont("Helvetica-Bold", 12)
            title = chart.get("spec", {}).get("title", f"Chart {i+1}")
            c.drawString(50, y_position, f"Chart: {title}")
            y_position -= 220 # Reserve space for image
            
            img_data = chart.get("png")
            if img_data:
                try:
                    img_bytes = base64.b64decode(img_data)
                    img_buffer = io.BytesIO(img_bytes)
                    img = ImageReader(img_buffer)
                    # Draw image (x, y, width, height)
                    c.drawImage(img, 50, y_position, width=400, height=200)
                except Exception as e:
                    c.drawString(50, y_position + 100, f"[Image Error: {e}]")
            
            y_position -= 30

        c.save()
        return filepath

    except Exception as e:
        print(f"[PDF Tool] Generation Failed: {e}")
        return ""