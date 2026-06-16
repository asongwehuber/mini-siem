from app.database.models import Log, Alert, QuarantinedHost


# =========================
# CRITICAL ALERT SUMMARY (LIGHTWEIGHT)
# =========================
def get_critical_alert_summary(limit=3):
    alerts = (
        Alert.query
        .filter_by(severity="CRITICAL")
        .order_by(Alert.timestamp.desc())
        .limit(limit)
        .all()
    )

    if not alerts:
        return "No critical alerts"

    return "\n".join(
        f"{a.alert_name} | {a.source_ip} | {a.status}"
        for a in alerts
    )


def build_siem_context() -> str:
    """
    Lightweight SIEM context optimized for LLM performance.
    """

    # =========================
    # METRICS
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
    # ATTACK PATTERNS (LIMITED)
    # =========================
    patterns = []

    if open_alerts > 10 and critical_alerts > 3:
        patterns.append("BRUTE FORCE")

    if critical_alerts > 5:
        patterns.append("CRITICAL SPIKE")

    if total_alerts > 50 and high_alerts > medium_alerts:
        patterns.append("SCANNING ACTIVITY")

    if quarantined_hosts > 0:
        patterns.append("HOSTS QUARANTINED")

    if not patterns:
        patterns.append("NO PATTERN")

    # keep only top 3 patterns (VERY IMPORTANT)
    patterns = patterns[:3]

    # =========================
    # RISK SCORE
    # =========================
    risk_score = (
        critical_alerts * 5 +
        high_alerts * 3 +
        medium_alerts +
        open_alerts * 2 +
        quarantined_hosts * 10
    )

    risk_score = min(risk_score, 100)

    if risk_score >= 75:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # =========================
    # CRITICAL ALERTS ONLY (LIMITED)
    # =========================
    critical_summary = get_critical_alert_summary(3)

    # =========================
    # FINAL CONTEXT (MINIMAL FORMAT)
    # =========================
    context = f"""
SYSTEM
Logs={total_logs}
Alerts={total_alerts}

STATUS
Open={open_alerts}
Closed={closed_alerts}

SEVERITY
C={critical_alerts} H={high_alerts} M={medium_alerts} L={low_alerts}

RISK
Score={risk_score}/100
Level={risk_level}

PATTERNS
{", ".join(patterns)}

CRITICAL
{critical_summary}
"""

    return context.strip()