from app.main import create_app
from app.reporting.report_generator import generate_report_data
from app.reporting.pdf_generator import create_pdf_report

app = create_app()

with app.app_context():
    data = generate_report_data("daily")
    create_pdf_report(data, "daily_security_report.pdf")

print("Daily report generated successfully")