from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import base64
import os
import uuid

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '../orchestrator/reports')

def generate_pdf_report(history: list) -> str:
    """
    Generates a PDF report containing insights, forecast, and charts for the entire session history.
    Returns the absolute path to the generated PDF.
    """
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # Title Page
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height / 2 + 50, "AI Data Analyst Report")
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2, height / 2, "Comprehensive Session Report")
        c.showPage()

        for i, item in enumerate(history):
            # New page for each query if not the first (or just continuous flow?)
            # Let's do continuous flow but ensure title separation
            
            y_position = height - 50
            
            # Query Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y_position, f"Query {i+1}: {item.get('user_query', 'N/A')}")
            y_position -= 30
            
            # Insights
            insights = item.get("insight_agent", {}).get("insights", "No insights generated.")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, "Insights:")
            y_position -= 15
            c.setFont("Helvetica", 10)
            
            text_object = c.beginText(50, y_position)
            text_object.setFont("Helvetica", 10)
            lines = insights.split('\n')
            for line in lines:
                while len(line) > 90:
                    text_object.textLine(line[:90])
                    line = line[90:]
                text_object.textLine(line)
            c.drawText(text_object)
            
            y_position = text_object.getY() - 20

            # Forecast
            forecast = item.get("forecast_agent", {}).get("forecast_text", "")
            if forecast and forecast != "No forecast generated.":
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "Forecast:")
                y_position -= 15
                
                text_object = c.beginText(50, y_position)
                text_object.setFont("Helvetica", 10)
                lines = forecast.split('\n')
                for line in lines:
                    while len(line) > 90:
                        text_object.textLine(line[:90])
                        line = line[90:]
                    text_object.textLine(line)
                c.drawText(text_object)
                y_position = text_object.getY() - 20

            # Charts
            charts = item.get("chart_agent", {}).get("charts", [])
            for j, chart in enumerate(charts):
                if y_position < 250:
                    c.showPage()
                    y_position = height - 50
                
                c.setFont("Helvetica-Bold", 10)
                title = chart.get("spec", {}).get("title", f"Chart {j+1}")
                c.drawString(50, y_position, f"Chart: {title}")
                y_position -= 210
                
                img_data = chart.get("png")
                if img_data:
                    try:
                        img_bytes = base64.b64decode(img_data)
                        img_buffer = io.BytesIO(img_bytes)
                        img = ImageReader(img_buffer)
                        c.drawImage(img, 50, y_position, width=400, height=200)
                    except Exception as e:
                        c.drawString(50, y_position + 100, f"[Image Error: {e}]")
                
                y_position -= 30
            
            # Separator between queries
            c.showPage()

        c.save()
        return filepath

    except Exception as e:
        print(f"[PDF Tool] Generation Failed: {e}")
        return ""