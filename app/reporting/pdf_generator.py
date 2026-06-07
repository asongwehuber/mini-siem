from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image
import os

from app.reporting.chart_generator import generate_severity_chart


def create_pdf_report(data, filename):

    data = data or {}

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("MINI SIEM SECURITY REPORT", styles['Title']))
    elements.append(Spacer(1, 12))

    # Report Info
    elements.append(Paragraph(
        f"Report Type: {data.get('report_type', 'N/A').upper()}",
        styles['Normal']
    ))

    elements.append(Paragraph(
        f"Generated At: {data.get('generated_at', 'N/A')}",
        styles['Normal']
    ))

    elements.append(Spacer(1, 20))

    #Executive summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))

    summary_text = (
        f"This {data.get('report_type', 'daily')} report recorded "
        f"{data.get('total_logs', 0)} log events and "
        f"{data.get('total_alerts', 0)} security alerts. "
        f"{data.get('critical_alerts', 0)} critical alerts were detected. "
        f"There are currently {data.get('quarantined_hosts', 0)} quarantined hosts."
    )

    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 20))



    # Summary
    elements.append(Paragraph("SUMMARY", styles['Heading2']))

    elements.append(Paragraph(f"Total Logs: {data.get('total_logs', 0)}", styles['Normal']))
    elements.append(Paragraph(f"Total Alerts: {data.get('total_alerts', 0)}", styles['Normal']))
    elements.append(Paragraph(f"Critical Alerts: {data.get('critical_alerts', 0)}", styles['Normal']))
    elements.append(Paragraph(f"High Alerts: {data.get('high_alerts', 0)}", styles['Normal']))
    elements.append(Paragraph(f"Medium Alerts: {data.get('medium_alerts', 0)}", styles['Normal']))
    elements.append(Paragraph(f"Low Alerts: {data.get('low_alerts', 0)}", styles['Normal']))
    elements.append(Paragraph(f"Quarantined Hosts: {data.get('quarantined_hosts', 0)}", styles['Normal']))

    elements.append(Spacer(1, 20))


    # Top Attackers
    elements.append(Paragraph("TOP ATTACKERS", styles['Heading2']))

    top_attackers = data.get("top_attackers", [])

    if not top_attackers:
        elements.append(
            Paragraph("No attacker activity detected.", styles['Normal'])
        )
    else:
        for ip, count in top_attackers:
            elements.append(
                Paragraph(
                    f"{ip} : {count} events",
                    styles['Normal']
                )
            )

    elements.append(Spacer(1, 20))


    # Top Ports
    elements.append(Paragraph("TOP PORTS", styles['Heading2']))

    top_ports = data.get("top_ports", [])

    if not top_ports:
        elements.append(
            Paragraph("No suspicious ports detected.", styles['Normal'])
        )
    else:
        for port, count in top_ports:
            elements.append(
                Paragraph(
                    f"Port {port} : {count} hits",
                    styles['Normal']
                )
            )

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("RECENT ALERTS", styles['Heading2']))

    recent_alerts = data.get("recent_alerts", [])

    if not recent_alerts:
        elements.append(
            Paragraph("No recent alerts.", styles['Normal'])
        )
    else:
        for alert in recent_alerts:
            elements.append(
                Paragraph(
                    f"{alert['timestamp']} | "
                    f"{alert['severity']} | "
                    f"{alert['name']}",
                    styles['Normal']
                )
            )


    #Risk assessment
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("RISK ASSESSMENT", styles['Heading2']))

    critical = data.get('critical_alerts', 0)
    high = data.get('high_alerts', 0)

    if critical > 0:
        risk_level = "CRITICAL"
    elif high > 5:
        risk_level = "HIGH"
    elif high > 0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    elements.append(
        Paragraph(
            f"Current Security Risk Level: {risk_level}",
            styles['Normal']
        )
    )

    # Severity Chart
    chart_file = "severity_chart.png"

    generate_severity_chart(
        data,
        chart_file
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "ALERT SEVERITY DISTRIBUTION",
            styles['Heading2']
        )
    )

    elements.append(
        Image(
            chart_file,
            width=400,
            height=250
        )
    )

    #report footer
    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            "Generated automatically by MINI-SIEM Reporting Engine",
            styles['Italic']
        )
    )

    # Build PDF
    doc.build(elements)