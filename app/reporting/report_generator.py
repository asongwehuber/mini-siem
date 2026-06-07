from datetime import datetime, timedelta
from collections import Counter

from app.database.models import Log, Alert, QuarantinedHost


def generate_report_data(report_type="daily"):

    now = datetime.utcnow()

    if report_type == "daily":
        start_date = now - timedelta(days=1)

    elif report_type == "weekly":
        start_date = now - timedelta(days=7)

    elif report_type == "monthly":
        start_date = now - timedelta(days=30)

    else:
        start_date = now - timedelta(days=1)

    # Fetch logs
    logs = Log.query.filter(
        Log.timestamp >= start_date
    ).all()

    # Fetch alerts
    alerts = Alert.query.filter(
        Alert.timestamp >= start_date
    ).all()

    # Fetch quarantined hosts
    quarantined_hosts = QuarantinedHost.query.all()

    # Severity counts
    critical_count = sum(
        1 for a in alerts
        if a.severity and a.severity.lower() == "critical"
    )

    high_count = sum(
        1 for a in alerts
        if a.severity and a.severity.lower() == "high"
    )

    medium_count = sum(
        1 for a in alerts
        if a.severity and a.severity.lower() == "medium"
    )

    low_count = sum(
        1 for a in alerts
        if a.severity and a.severity.lower() == "low"
    )

    # Top attackers
    attacker_ips = [
        log.source_ip
        for log in logs
        if log.source_ip
    ]

    top_attackers = Counter(attacker_ips).most_common(5)

    # Top ports
    ports = [
        str(log.destination_port)
        for log in logs
        if log.destination_port
    ]

    top_ports = Counter(ports).most_common(5)

    # Recent alerts
    recent_alerts = Alert.query.order_by(
        Alert.timestamp.desc()
    ).limit(5).all()

    return {
        "report_type": report_type,
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),

        "total_logs": len(logs),
        "total_alerts": len(alerts),

        "critical_alerts": critical_count,
        "high_alerts": high_count,
        "medium_alerts": medium_count,
        "low_alerts": low_count,

        "quarantined_hosts": len(quarantined_hosts),

        "top_attackers": top_attackers,
        "top_ports": top_ports,

        "recent_alerts": [
            {
                "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if a.timestamp else "N/A",
                "name": a.alert_name or "Unknown Alert",
                "severity": a.severity or "Unknown"
            }
            for a in recent_alerts
        ]
    }