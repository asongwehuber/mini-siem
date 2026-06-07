from datetime import datetime, timedelta
from app.response.quarantine import quarantine_host
from flask_mail import Message
from app.extensions import mail
from app.extensions import db
from app.database.models import Log, Alert


# =========================================
# NORMALIZATION
# =========================================
def normalize_severity(sev):
    if not sev:
        return "low"
    return sev.lower()


# =========================================
# EMAIL ALERT
# =========================================
def send_alert_email(alert):

    try:
        msg = Message(
            subject=f"🚨 Mini-SIEM Alert: {alert.alert_name}",
            recipients=["huber.asongwe@gmail.com",
                       # "reinette.mengue@compost.cm"  do not remove this mail, I will uncomment it later
                       # "reinettemengue@gmail.com"   do not remove this mail, I will uncomment it later
                        
                        ]
        )

        msg.body = f"""
ALERT GENERATED

Alert Name: {alert.alert_name}
Severity: {alert.severity}
Source IP: {alert.source_ip}
Event Count: {alert.event_count}

Description:
{alert.description}

Timestamp:
{alert.timestamp}
"""

        mail.send(msg)

        print(f"[EMAIL] Sent for {alert.alert_name}")

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


# =========================================
# BRUTE FORCE DETECTION
# =========================================
def detect_brute_force(source_ip):

    one_minute_ago = datetime.utcnow() - timedelta(seconds=60)

    failed_logins = Log.query.filter(
        Log.source_ip == source_ip,
        Log.event_type.ilike('failed_login'),
        Log.timestamp >= one_minute_ago
    ).count()
    print("[BRUTE FORCE CHECK] failed_logins =", failed_logins)

    print(f"[DEBUG] Failed logins: {failed_logins}")

    if failed_logins >= 5:

        existing_alert = Alert.query.filter_by(
            source_ip=source_ip,
            alert_name='Brute Force Attack',
            status='open'
        ).first()

        if existing_alert:

            existing_alert.event_count += 1

            if existing_alert.event_count >= 20:
                existing_alert.severity = normalize_severity('critical')
            elif existing_alert.event_count >= 10:
                existing_alert.severity = normalize_severity('high')
            else:
                existing_alert.severity = normalize_severity('medium')

            db.session.commit()

        else:

            alert = Alert(
                alert_name='Brute Force Attack',
                description=f'Failed logins from {source_ip}',
                severity=normalize_severity('medium'),
                source_ip=source_ip,
                event_count=1,
                status='open'
            )

            db.session.add(alert)
            db.session.commit()

            send_alert_email(alert)


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
    print("[PORT SCAN CHECK] unique ports =", len(unique_ports))

    for log in logs:
        if log.destination_port:
            unique_ports.add(log.destination_port)

    print(f"[DEBUG] Ports scanned: {len(unique_ports)}")

    if len(unique_ports) >= 5:

        existing_alert = Alert.query.filter_by(
            source_ip=source_ip,
            alert_name='Possible Port Scan',
            status='open'
        ).first()

        if existing_alert:

            existing_alert.event_count += 1

            if existing_alert.event_count >= 20:
                existing_alert.severity = normalize_severity('critical')
            elif existing_alert.event_count >= 10:
                existing_alert.severity = normalize_severity('high')
            else:
                existing_alert.severity = normalize_severity('medium')

            db.session.commit()

        else:

            alert = Alert(
                alert_name='Possible Port Scan',
                description=f'Ports: {list(unique_ports)}',
                severity=normalize_severity('medium'),
                source_ip=source_ip,
                event_count=1,
                status='open'
            )

            db.session.add(alert)
            db.session.commit()

            send_alert_email(alert)


# =========================================
# HIGH SEVERITY INCIDENT
# =========================================
def detect_high_severity_incident(source_ip, hostname):

    two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)

    high_logs = Log.query.filter(
        Log.source_ip == source_ip,
        Log.severity.in_(['high', 'critical']),
        Log.timestamp >= two_minutes_ago
    ).all()
    print("[HIGH SEV CHECK] logs =", len(high_logs))

    print(f"[DEBUG] High logs: {len(high_logs)}")

    if len(high_logs) >= 3:

        existing_alert = Alert.query.filter_by(
            source_ip=source_ip,
            alert_name='Critical Security Incident',
            status='open'
        ).first()

        if existing_alert:

            existing_alert.event_count += 1

            if existing_alert.event_count >= 20:
                existing_alert.severity = normalize_severity('critical')
            elif existing_alert.event_count >= 10:
                existing_alert.severity = normalize_severity('high')
            else:
                existing_alert.severity = normalize_severity('medium')

            db.session.commit()

        else:

            alert = Alert(
                alert_name='Critical Security Incident',
                description=f'High severity events from {source_ip}',
                severity=normalize_severity('critical'),
                source_ip=source_ip,
                event_count=1,
                status='open'
            )

            db.session.add(alert)
            db.session.commit()

            send_alert_email(alert)

            quarantine_host(
                ip=source_ip,
                hostname=hostname,
                reason="Critical Security Incident"
            )

            print(f"[ALERT] Critical incident: {source_ip}")