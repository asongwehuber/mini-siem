import requests
import re

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:8b"

def clean_response(text):
    text = re.sub(r"[*#`_]+", "", text)
    return text.strip()

def ask_ai(prompt):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        answer = response.json()["response"]
        return clean_response(answer)

    except Exception as e:
        return f"AI Error: {str(e)}"