from flask_mail import Message
from app.extensions import mail
from zoneinfo import ZoneInfo





ALERT_RECIPIENTS = [
    "huber.asongwe@gmail.com",
    # "reinette.mengue@campost.cm",
    # "reinettemengue@gmail.com"
]

def send_alert_email(alert):

    local_time = alert.timestamp.replace(
        tzinfo=ZoneInfo("UTC")
    ).astimezone(
        ZoneInfo("Africa/Douala")
    )

    msg = Message(
        subject=f"🚨 Mini-SIEM Alert: {alert.alert_name}",
        recipients=ALERT_RECIPIENTS
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
{local_time.strftime('%d-%m-%Y %H:%M:%S ')}
"""

    mail.send(msg)