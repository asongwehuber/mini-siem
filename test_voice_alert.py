import os
import requests
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

alert_text = """
Critical security alert.
Possible brute force attack detected.
Immediate investigation required.
"""

tts = gTTS(text=alert_text, lang="en")
tts.save("alert.mp3")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"

with open("alert.mp3", "rb") as audio:
    response = requests.post(
        url,
        data={"chat_id": CHAT_ID},
        files={"audio": audio}
    )

print(response.json())