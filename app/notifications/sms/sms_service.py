import logging

from app.notifications.sms.simulated_sms import sms_provider

# FUTURE: when orange gived credentials, upper line will be removed and lover line will be uncommented
# from app.notifications.sms.orange_sms import sms_provider


logging.basicConfig(
    filename="sms.log",
    level=logging.INFO
)


SOC_PHONES = [
    "+2376XXXXXXXX",
    "+2376YYYYYYYY"
]


def build_sms_message(alert):

    geo = getattr(alert, "geo", None)

    location_text = "Unknown"

    if geo and isinstance(geo, dict):
        city = geo.get("city", "Unknown")
        country = geo.get("country", "Unknown")
        location_text = f"{city}, {country}"

    return (
        f"MINI-SIEM ALERT\n"
        f"Alert: {alert.alert_name}\n"
        f"IP: {alert.source_ip}\n"
        f"Location: {location_text}\n"
        f"Severity: {str(alert.severity).upper()}"
    )


def send_sms(phone, message):

    success = sms_provider.send_sms(
        phone,
        message
    )

    if success:

        logging.info(
            f"SMS sent to {phone}"
        )

    else:

        logging.error(
            f"SMS failed to {phone}"
        )

    return success


def send_alert_sms(alert):

    message = build_sms_message(alert)

    for phone in SOC_PHONES:

        send_sms(
            phone,
            message
        )