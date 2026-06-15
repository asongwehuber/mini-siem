from app.database.models import Log, Alert, QuarantinedHost
from sqlalchemy import func


def build_siem_context() -> str:
    """
    Builds SIEM context with attack pattern labeling and risk scoring.
    """

    # =========================
    # BASIC METRICS
    # =========================
    total_logs = Log.query.count()
    total_alerts = Alert.query.count()

    open_alerts = Alert.query.filter_by(status="OPEN").count()
    closed_alerts = Alert.query.filter_by(status="CLOSED").count()

    critical_alerts = Alert.query.filter_by(severity="CRITICAL").count()
    high_alerts = Alert.query.filter_by(severity="HIGH").count()
    medium_alerts = Alert.query.filter_by(severity="MEDIUM").count()
    low_alerts = Alert.query.filter_by(severity="LOW").count()

    quarantined_hosts = QuarantinedHost.query.filter_by(
        status="quarantined"
    ).count()

    # =========================
    # ATTACK PATTERN DETECTION (RULE-BASED)
    # =========================
    patterns = []

    # Brute force detection
    if open_alerts > 10 and critical_alerts > 3:
        patterns.append("Possible BRUTE FORCE ATTACK")

    # High severity spike
    if critical_alerts > 5:
        patterns.append("CRITICAL ALERT SPIKE (possible active intrusion)")

    # Suspicious scanning behavior
    if total_alerts > 50 and high_alerts > medium_alerts:
        patterns.append("POSSIBLE NETWORK SCANNING ACTIVITY")

    # Quarantine indication
    if quarantined_hosts > 0:
        patterns.append("MALICIOUS HOSTS QUARANTINED")

    if not patterns:
        patterns.append("No clear attack pattern detected")

    # =========================
    # RISK SCORE CALCULATION (0–100)
    # =========================
    risk_score = 0

    # severity weight
    risk_score += critical_alerts * 5
    risk_score += high_alerts * 3
    risk_score += medium_alerts * 1

    # open alerts increase risk
    risk_score += open_alerts * 2

    # quarantined hosts strongly increase risk
    risk_score += quarantined_hosts * 10

    # cap score
    risk_score = min(risk_score, 100)

    # risk level interpretation
    if risk_score >= 75:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # =========================
    # RECENT ALERTS
    # =========================
    recent_alerts = (
        Alert.query
        .order_by(Alert.timestamp.desc())
        .limit(10)
        .all()
    )

    alert_summary = "\n".join(
        f"- {a.timestamp} | {a.alert_name} | {a.severity} | {a.source_ip} | {a.status}"
        for a in recent_alerts
    ) if recent_alerts else "No recent alerts."

    # =========================
    # CONTEXT OUTPUT
    # =========================
    context = f"""
==================== SYSTEM STATUS ====================

Total Logs: {total_logs}
Total Alerts: {total_alerts}

Alert Breakdown:
- Open: {open_alerts}
- Closed: {closed_alerts}

Severity Breakdown:
- Critical: {critical_alerts}
- High: {high_alerts}
- Medium: {medium_alerts}
- Low: {low_alerts}

Quarantined Hosts: {quarantined_hosts}

==================== SECURITY ANALYSIS ====================

Risk Score: {risk_score}/100
Risk Level: {risk_level}

Detected Attack Patterns:
- {chr(10).join(patterns)}

==================== RECENT ALERTS ====================
{alert_summary}
"""

    return context.strip()