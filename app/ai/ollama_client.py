import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:8b"


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

        return response.json()["response"]

    except Exception as e:
        return f"AI Error: {str(e)}"