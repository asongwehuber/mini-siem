from datetime import datetime, timedelta

from app.extensions import db
from app.database.models import Log, Alert
from app.notifications.alert_dispatcher import dispatch_alert
from app.response.quarantine import quarantine_host


# =========================================
# NORMALIZATION
# =========================================

def normalize_severity(sev):
    if not sev:
        return "low"
    return sev.lower()


# =========================================
# ALERT ESCALATION HELPER
# =========================================

def update_alert_severity(alert):

    old_severity = alert.severity

    if alert.event_count >= 20:
        alert.severity = normalize_severity("critical")

    elif alert.event_count >= 10:
        alert.severity = normalize_severity("high")

    else:
        alert.severity = normalize_severity("medium")

    db.session.commit()

    if old_severity != alert.severity:
        dispatch_alert(alert)


# =========================================
# BRUTE FORCE DETECTION
# =========================================

def detect_brute_force(source_ip):

    one_minute_ago = datetime.utcnow() - timedelta(seconds=60)

    failed_logins = Log.query.filter(
        Log.source_ip == source_ip,
        Log.event_type.ilike("failed_login"),
        Log.timestamp >= one_minute_ago
    ).count()

    print(f"[BRUTE FORCE CHECK] failed_logins = {failed_logins}")

    if failed_logins < 5:
        return

    existing_alert = Alert.query.filter_by(
        source_ip=source_ip,
        alert_name="Brute Force Attack",
        status="open"
    ).first()

    if existing_alert:

        existing_alert.event_count += 1

        update_alert_severity(existing_alert)

        return

    alert = Alert(
        alert_name="Brute Force Attack",
        description=f"Failed logins from {source_ip}",
        severity=normalize_severity("medium"),
        source_ip=source_ip,
        event_count=1,
        status="open"
    )

    db.session.add(alert)
    db.session.commit()

    dispatch_alert(alert)


# =========================================
# PORT SCAN DETECTION
# =========================================

def detect_port_scan(source_ip):

    thirty_seconds_ago = datetime.utcnow() - timedelta(seconds=30)

    logs = Log.query.filter(
        Log.source_ip == source_ip,
        Log.timestamp >= thirty_seconds_ago
    ).all()

    unique_ports = set()

    for log in logs:
        if log.destination_port:
            unique_ports.add(log.destination_port)

    print(f"[PORT SCAN CHECK] unique ports = {len(unique_ports)}")

    if len(unique_ports) < 5:
        return

    existing_alert = Alert.query.filter_by(
        source_ip=source_ip,
        alert_name="Possible Port Scan",
        status="open"
    ).first()

    if existing_alert:

        existing_alert.event_count += 1

        update_alert_severity(existing_alert)

        return

    alert = Alert(
        alert_name="Possible Port Scan",
        description=f"Ports: {list(unique_ports)}",
        severity=normalize_severity("medium"),
        source_ip=source_ip,
        event_count=1,
        status="open"
    )

    db.session.add(alert)
    db.session.commit()

    dispatch_alert(alert)


# =========================================
# HIGH SEVERITY INCIDENT
# =========================================

def detect_high_severity_incident(source_ip, hostname):

    two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)

    high_logs = Log.query.filter(
        Log.source_ip == source_ip,
        Log.severity.in_(["high", "critical"]),
        Log.timestamp >= two_minutes_ago
    ).all()

    print(f"[HIGH SEVERITY CHECK] logs = {len(high_logs)}")

    if len(high_logs) < 3:
        return

    existing_alert = Alert.query.filter_by(
        source_ip=source_ip,
        alert_name="Critical Security Incident",
        status="open"
    ).first()

    if existing_alert:

        existing_alert.event_count += 1

        update_alert_severity(existing_alert)

        return

    alert = Alert(
        alert_name="Critical Security Incident",
        description=f"High severity events from {source_ip}",
        severity=normalize_severity("critical"),
        source_ip=source_ip,
        event_count=1,
        status="open"
    )

    db.session.add(alert)
    db.session.commit()

    dispatch_alert(alert)

    quarantine_host(
        ip=source_ip,
        hostname=hostname,
        reason="Critical Security Incident"
    )

    print(f"[ALERT] Critical incident detected from {source_ip}")