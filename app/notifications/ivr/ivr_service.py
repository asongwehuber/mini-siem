import logging

from app.notifications.ivr.simulated_ivr import ivr_provider

logging.basicConfig(
    filename="ivr.log",
    level=logging.INFO
)

SOC_PHONES = [
    "+2376XXXXXXXX"
]


def make_call(phone, alert):

    success = ivr_provider.make_call(
        phone,
        alert
    )

    if success:
        logging.info(
            f"IVR call placed to {phone}"
        )

    return success


def send_alert_ivr(alert):

    for phone in SOC_PHONES:

        make_call(
            phone,
            alert
        )