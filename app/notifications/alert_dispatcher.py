from app.notifications.email_alert import send_alert_email
from app.notifications.telegram_alert import (
    send_alert_telegram,
    send_alert_voice
)
from app.notifications.sms.sms_service import send_alert_sms
from app.notifications.ivr.ivr_service import send_alert_ivr


def dispatch_alert(alert):

    send_alert_email(alert)

    send_alert_telegram(alert)

    if alert.severity == "critical":

        send_alert_voice(alert)

        send_alert_sms(alert)

        send_alert_ivr(alert)