import requests
import re

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:8b"

def clean_response(text: str) -> str:
    """
    Remove markdown-like formatting and normalize output.
    """
    text = re.sub(r"[*#`_]+", "", text)
    return text.strip()

def ask_ai(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=600  # increased for heavy SIEM prompts
        )

        # Raise error if Ollama fails
        response.raise_for_status()

        data = response.json()

        # safer extraction (Ollama sometimes returns partial structures)
        answer = data.get("response", "")

        if not answer:
            return "AI Error: Empty response from model"

        return clean_response(answer)

    except requests.exceptions.Timeout:
        return "AI Error: Ollama request timed out. Try reducing SIEM context size."

    except requests.exceptions.ConnectionError:
        return "AI Error: Cannot connect to Ollama. Is it running on localhost:11434?"

    except Exception as e:
        return f"AI Error: {str(e)}"