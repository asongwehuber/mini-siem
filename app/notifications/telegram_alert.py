import os
import tempfile
import requests

from gtts import gTTS
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_alert_telegram(alert):

    local_time = alert.timestamp.replace(
        tzinfo=ZoneInfo("UTC")
    ).astimezone(
        ZoneInfo("Africa/Douala")
    )

    message = f"""
🚨 MINI-SIEM ALERT

Alert Name: {alert.alert_name}
Severity: {alert.severity.upper()}
Source IP: {alert.source_ip}
Event Count: {alert.event_count}

Description:
{alert.description}

Timestamp:
{local_time.strftime('%d-%m-%Y %H:%M:%S')}
"""

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
    )


def send_alert_voice(alert):

    voice_text = (
        f"Critical security alert. "
        f"{alert.alert_name}. "
        f"{alert.description}. "
        f"Immediate investigation required."
    )

    with tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    ) as temp_file:

        filename = temp_file.name

    gTTS(
        text=voice_text,
        lang="en"
    ).save(filename)

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendAudio"
    )

    with open(filename, "rb") as audio:

        requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID
            },
            files={
                "audio": audio
            }
        )

    os.remove(filename)