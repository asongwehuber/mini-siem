import logging
from app.notifications.ivr.simulated_ivr import ivr_provider

logging.basicConfig(
    filename="ivr.log",
    level=logging.INFO
)

SOC_PHONES = [
    "+2376XXXXXXXX"
]


# =========================================
# FORMAT IVR MESSAGE (IMPORTANT FIX)
# =========================================

def build_ivr_message(alert):

    geo = getattr(alert, "geo", None)

    location_text = "Unknown"

    if geo and isinstance(geo, dict):
        city = geo.get("city", "Unknown")
        country = geo.get("country", "Unknown")
        location_text = f"{city}, {country}"

    return (
        f"Critical Security Alert. "
        f"Alert: {alert.alert_name}. "
        f"Source IP: {alert.source_ip}. "
        f"Location: {location_text}. "
        f"Severity: {str(alert.severity).upper()}. "
        f"Please respond immediately."
    )


# =========================================
# MAKE CALL
# =========================================

def make_call(phone, message):

    try:
        success = ivr_provider.make_call(
            phone,
            message
        )

        if success:
            logging.info(f"IVR call placed to {phone}")
        else:
            logging.error(f"IVR call failed to {phone}")

        return success

    except Exception as e:
        logging.error(f"IVR exception for {phone}: {e}")
        return False


# =========================================
# DISPATCH IVR ALERT
# =========================================

def send_alert_ivr(alert):

    message = build_ivr_message(alert)

    for phone in SOC_PHONES:

        make_call(phone, message)