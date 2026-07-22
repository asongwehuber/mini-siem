from flask_mail import Message
from app.extensions import mail
from zoneinfo import ZoneInfo


ALERT_RECIPIENTS = [
    #"huber.asongwe@gmail.com",
    #"reinette.mengue@campost.cm",
    #"reinettemengue@gmail.com"
]


def send_alert_email(alert):

    # Disable email if no recipients configured
    if not ALERT_RECIPIENTS:
        print("Email alert skipped: no recipients configured")
        return

    # -----------------------------
    # TIMEZONE CONVERSION
    # -----------------------------
    local_time = alert.timestamp.replace(
        tzinfo=ZoneInfo("UTC")
    ).astimezone(
        ZoneInfo("Africa/Douala")
    )

    geo = getattr(alert, "geo", None)

    location_text = "Unknown"

    if geo and isinstance(geo, dict):
        city = geo.get("city", "Unknown")
        country = geo.get("country", "Unknown")
        location_text = f"{city}, {country}"


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



# =====================================
# SEND OTP EMAIL
# =====================================

def send_otp_email(admin, otp_code):

    msg = Message(
        subject="Mini SIEM - Password Reset OTP",
        recipients=[admin.email]
    )

    msg.body = f"""
Hello {admin.fullname},

A request was made to reset your Mini SIEM administrator password.

Your One-Time Password (OTP) is:

{otp_code}

This OTP is valid for 10 minutes.

If you did not request this password reset, please ignore this email.

Mini SIEM Security Team
"""

    mail.send(msg)