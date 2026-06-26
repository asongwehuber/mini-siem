from flask_mail import Message
from app.extensions import mail
from zoneinfo import ZoneInfo


ALERT_RECIPIENTS = [
    "huber.asongwe@gmail.com",
    # "reinette.mengue@campost.cm", do not remove this
    # "reinettemengue@gmail.com" do not remove this
]


def send_alert_email(alert):

    # -----------------------------
    # TIMEZONE CONVERSION
    # -----------------------------
    local_time = alert.timestamp.replace(
        tzinfo=ZoneInfo("UTC")
    ).astimezone(
        ZoneInfo("Africa/Douala")
    )

    # -----------------------------
    # GEOIP ENRICHMENT DISPLAY
    # -----------------------------
    geo = getattr(alert, "geo", None)

    location_text = "Unknown"

    if geo and isinstance(geo, dict):
        city = geo.get("city", "Unknown")
        country = geo.get("country", "Unknown")
        location_text = f"{city}, {country}"

    # -----------------------------
    # EMAIL MESSAGE
    # -----------------------------
    msg = Message(
        subject=f"🚨 Mini-SIEM Alert: {alert.alert_name}",
        recipients=ALERT_RECIPIENTS
    )

    msg.body = f"""
ALERT GENERATED

Alert Name: {alert.alert_name}
Severity: {alert.severity}
Source IP: {alert.source_ip}
Location: {location_text}
Event Count: {alert.event_count}

Description:
{alert.description}

Timestamp:
{local_time.strftime('%d-%m-%Y %H:%M:%S')}
"""

    mail.send(msg)