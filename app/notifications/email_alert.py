from flask_mail import Message


def send_alert_email(mail, alert):

    try:

        subject = f"[SIEM ALERT] {alert.alert_name}"

        body = f"""
Security Alert Generated

Alert Name:
{alert.alert_name}

Severity:
{alert.severity}

Source IP:
{alert.source_ip}

Description:
{alert.description}

Event Count:
{alert.event_count}

Status:
{alert.status}

Timestamp:
{alert.timestamp}

----------------------------------
Mini-SIEM Notification System
"""

        msg = Message(
            subject=subject,
            recipients=["huber.asongwe@gmail.com"]
        )

        msg.body = body

        mail.send(msg)

        print(
            f"[EMAIL] Alert notification sent for {alert.alert_name}"
        )

    except Exception as e:

        print(
            f"[EMAIL ERROR] {str(e)}"
        )
