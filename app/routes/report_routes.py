from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required 
import os

from app.reporting.report_generator import generate_report_data
from app.reporting.pdf_generator import create_pdf_report


report_bp = Blueprint("report_bp", __name__)


# =========================================
# JSON REPORT (for dashboard/API)
# =========================================
@report_bp.route("/report")
@login_required
def generate_report():

    report_type = request.args.get("type", "daily")

    data = generate_report_data(report_type)

    return jsonify(data)


# =========================================
# SIMPLE DAILY PDF DOWNLOAD
# =========================================
@report_bp.route("/reports/download")
@login_required
def download_daily_report():

    data = generate_report_data("daily")

    filename = os.path.join(
        os.getcwd(),
        "daily_security_report.pdf"
    )

    create_pdf_report(data, filename)

    return send_file(
        filename,
        as_attachment=True,
        download_name="daily_security_report.pdf"
    )


# =========================================
# PARAMETERIZED PDF REPORT
# =========================================
@report_bp.route("/report/pdf")
@login_required
def download_report_pdf():

    report_type = request.args.get("type", "daily")

    data = generate_report_data(report_type)

    filename = os.path.join(
        os.getcwd(),
        f"{report_type}_security_report.pdf"
    )

    create_pdf_report(data, filename)

    return send_file(
        filename,
        as_attachment=True,
        download_name=f"{report_type}_security_report.pdf"
    )


# =========================================
# TEST ROUTE
# =========================================
@report_bp.route("/report-test")
@login_required
def report_test():
    return {
        "status": "success",
        "message": "Reporting module loaded correctly"
    }