import os
import tempfile
import requests

from gtts import gTTS
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# =========================================
# TELEGRAM ALERT
# =========================================

def send_alert_telegram(alert):

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

    message = f"""
🚨 MINI-SIEM ALERT

Alert Name: {alert.alert_name}
Severity: {alert.severity.upper()}
Source IP: {alert.source_ip}
Location: {location_text}
Event Count: {alert.event_count}

Description:
{alert.description}

Timestamp:
{local_time.strftime('%d-%m-%Y %H:%M:%S')}
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=10
        )

        if not response.ok:
            print("[TELEGRAM ERROR]", response.text)

    except Exception as e:
        print("[TELEGRAM EXCEPTION]", e)


# =========================================
# VOICE ALERT
# =========================================

def send_alert_voice(alert):

    geo = getattr(alert, "geo", None)

    location_text = ""

    if geo and isinstance(geo, dict):
        location_text = f"{geo.get('city','Unknown')} in {geo.get('country','Unknown')}"

    voice_text = (
        f"Critical security alert. "
        f"{alert.alert_name}. "
        f"Source IP {alert.source_ip}. "
        f"Location {location_text}. "
        f"Severity {alert.severity}. "
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

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"

    try:
        with open(filename, "rb") as audio:
            requests.post(
                url,
                data={
                    "chat_id": TELEGRAM_CHAT_ID
                },
                files={
                    "audio": audio
                },
                timeout=15
            )

    except Exception as e:
        print("[VOICE ERROR]", e)

    finally:
        os.remove(filename)