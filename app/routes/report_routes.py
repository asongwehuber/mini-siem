from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required 
import os

from app.reporting.report_generator import generate_report_data
from app.reporting.pdf_generator import create_pdf_report

from app.database.models import Log, Alert, QuarantinedHost
from app.reporting.export_pdf import create_table_pdf
from app.reporting.csv_generator import create_csv
from app.routes.log_routes import format_time

from app.utils.time_filters import get_time_range
from datetime import datetime




# =========================================
# log filter helper
# =========================================

def get_filtered_logs():

    query = Log.query

    source_ip = request.args.get("source_ip")
    severity = request.args.get("severity")
    event_type = request.args.get("event_type")
    period = request.args.get("period")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if period and period != "custom":

        start, end = get_time_range(period)

        if start and end:

            query = query.filter(
                Log.timestamp >= start,
                Log.timestamp <= end
            )

    if period == "custom" and start_time and end_time:

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        query = query.filter(
            Log.timestamp >= start,
            Log.timestamp <= end
        )

    if source_ip:

        query = query.filter_by(
            source_ip=source_ip
        )

    if severity:

        query = query.filter_by(
            severity=severity
        )

    if event_type:

        query = query.filter_by(
            event_type=event_type
        )

    return query.order_by(
        Log.timestamp.desc()
    ).all()


report_bp = Blueprint("report_bp", __name__)


# =========================================
# Alerts filter helper
# =========================================

def get_filtered_alerts():

    query = Alert.query

    severity = request.args.get("severity")
    source_ip = request.args.get("source_ip")
    status = request.args.get("status")

    period = request.args.get("period")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")


    if period and period != "custom":

        start, end = get_time_range(period)

        if start and end:

            query = query.filter(
                Alert.timestamp >= start,
                Alert.timestamp <= end
            )


    if period == "custom" and start_time and end_time:

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        query = query.filter(
            Alert.timestamp >= start,
            Alert.timestamp <= end
        )


    if severity:
        query = query.filter_by(
            severity=severity
        )


    if source_ip:
        query = query.filter_by(
            source_ip=source_ip
        )


    if status:
        query = query.filter_by(
            status=status
        )


    return query.order_by(
        Alert.timestamp.desc()
    ).all()



# =========================================
# Quarantined host helper
# =========================================

def get_filtered_quarantined_hosts():

    query = QuarantinedHost.query


    status = request.args.get("status")

    search = request.args.get("search")

    period = request.args.get("period")

    start_time = request.args.get("start_time")

    end_time = request.args.get("end_time")



    # ==========================
    # TIME FILTER
    # ==========================

    if period and period != "custom":

        start, end = get_time_range(period)

        if start and end:

            query = query.filter(
                QuarantinedHost.quarantined_at >= start,
                QuarantinedHost.quarantined_at <= end
            )



    # ==========================
    # CUSTOM DATE FILTER
    # ==========================

    if period == "custom" and start_time and end_time:

        start = datetime.fromisoformat(
            start_time
        )

        end = datetime.fromisoformat(
            end_time
        )


        query = query.filter(
            QuarantinedHost.quarantined_at >= start,
            QuarantinedHost.quarantined_at <= end
        )



    # ==========================
    # STATUS FILTER
    # ==========================

    if status:

        query = query.filter_by(
            status=status
        )



    # ==========================
    # SEARCH FILTER
    # ==========================

    if search:

        query = query.filter(
            (QuarantinedHost.source_ip.like(
                f"%{search}%"
            ))
            |
            (QuarantinedHost.hostname.like(
                f"%{search}%"
            ))
        )



    return query.order_by(
        QuarantinedHost.quarantined_at.desc()
    ).all()







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



# =========================================
# csv export route for  logs
# =========================================

@report_bp.route("/logs/export/csv")
@login_required
def export_logs_csv():

    logs = get_filtered_logs()

    headers = [
        "Timestamp",
        "Source IP",
        "Hostname",
        "Event Type",
        "Severity",
        "Destination Port",
        "Message"
    ]

    rows = []

    for log in logs:

        rows.append([

            format_time(log.timestamp),

            log.source_ip,

            log.hostname,

            log.event_type,

            log.severity,

            log.destination_port,

            log.message

        ])

    filename = os.path.join(
        os.getcwd(),
        "logs.csv"
    )

    create_csv(
        headers,
        rows,
        filename
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name="logs.csv"
    )


# =========================================
# pdf export route for logs
# =========================================

@report_bp.route("/logs/export/pdf")
@login_required
def export_logs_pdf():

    logs = get_filtered_logs()

    headers = [
        "Timestamp",
        "Source IP",
        "Hostname",
        "Event",
        "Severity",
        "Port"
    ]

    rows = []

    for log in logs:

        rows.append([

            format_time(log.timestamp),

            log.source_ip,

            log.hostname,

            log.event_type,

            log.severity,

            str(log.destination_port)

        ])

    filename = os.path.join(
        os.getcwd(),
        "logs.pdf"
    )

    create_table_pdf(
        "Mini SIEM Logs Report",
        headers,
        rows,
        filename
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name="logs.pdf"
    )

# =========================================
# CSV EXPORT ALERTS
# =========================================

@report_bp.route("/alerts/export/csv")
@login_required
def export_alerts_csv():

    alerts = get_filtered_alerts()


    headers = [
        "Timestamp",
        "Alert Name",
        "Description",
        "Severity",
        "Source IP",
        "Event Count",
        "Status"
    ]


    rows = []


    for alert in alerts:

        rows.append([

            format_time(alert.timestamp),

            alert.alert_name,

            alert.description,

            alert.severity,

            alert.source_ip,

            alert.event_count,

            alert.status

        ])


    filename = os.path.join(
        os.getcwd(),
        "alerts.csv"
    )


    create_csv(
        headers,
        rows,
        filename
    )


    return send_file(
        filename,
        as_attachment=True,
        download_name="alerts.csv"
    )



# =========================================
# PDF EXPORT ALERTS
# =========================================

@report_bp.route("/alerts/export/pdf")
@login_required
def export_alerts_pdf():

    alerts = get_filtered_alerts()


    headers = [
        "Timestamp",
        "Alert",
        "Severity",
        "Source IP",
        "Count",
        "Status"
    ]


    rows = []


    for alert in alerts:

        rows.append([

            format_time(alert.timestamp),

            alert.alert_name,

            alert.severity,

            alert.source_ip,

            str(alert.event_count),

            alert.status

        ])


    filename = os.path.join(
        os.getcwd(),
        "alerts.pdf"
    )


    create_table_pdf(
        "Mini SIEM Alerts Report",
        headers,
        rows,
        filename
    )


    return send_file(
        filename,
        as_attachment=True,
        download_name="alerts.pdf"
    )

# =========================================
# CSV EXPORT QUARANTINED HOSTS
# =========================================

@report_bp.route("/quarantine/export/csv")
@login_required
def export_quarantine_csv():

    hosts = get_filtered_quarantined_hosts()


    headers = [
        "Hostname",
        "Source IP",
        "Reason",
        "Status",
        "Quarantined At"
    ]


    rows = []


    for host in hosts:

        rows.append([

            host.hostname,

            host.source_ip,

            host.reason,

            host.status,

            format_time(
                host.quarantined_at
            )

        ])


    filename = os.path.join(
        os.getcwd(),
        "quarantined_hosts.csv"
    )


    create_csv(
        headers,
        rows,
        filename
    )


    return send_file(
        filename,
        as_attachment=True,
        download_name="quarantined_hosts.csv"
    )


# =========================================
# PDF EXPORT QUARANTINED HOSTS
# =========================================

@report_bp.route("/quarantine/export/pdf")
@login_required
def export_quarantine_pdf():

    hosts = get_filtered_quarantined_hosts()


    headers = [
        "Hostname",
        "Source IP",
        "Reason",
        "Status",
        "Quarantined At"
    ]


    rows = []


    for host in hosts:

        rows.append([

            host.hostname or "-",

            host.source_ip,

            host.reason,

            host.status,

            format_time(
                host.quarantined_at
            )

        ])



    filename = os.path.join(
        os.getcwd(),
        "quarantined_hosts.pdf"
    )


    create_table_pdf(

        "Mini SIEM Quarantined Hosts Report",

        headers,

        rows,

        filename

    )


    return send_file(

        filename,

        as_attachment=True,

        download_name="quarantined_hosts.pdf"

    )