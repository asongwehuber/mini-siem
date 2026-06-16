from app.ai.siem_context import build_siem_context
from flask import Blueprint, request, jsonify
from app.ai.ollama_client import ask_ai

chat_bp = Blueprint("chat", __name__)


def needs_siem_context(message: str) -> bool:
    """
    Decide whether SIEM context is required.
    """
    keywords = [
        "alert", "alerts", "log", "logs", "attack", "intrusion",
        "quarantine", "host", "ip", "incident", "risk", "severity",
        "brute", "scan", "malware", "breach", "incident", "threat"
    ]
    msg = message.lower()
    return any(k in msg for k in keywords)


@chat_bp.route("/ai/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a question"
        })

    # =========================
    # SMART CONTEXT LOADING
    # =========================
    context = ""

    if needs_siem_context(message):
        context = build_siem_context()

        MAX_CONTEXT_CHARS = 7000
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS].rsplit("\n", 1)[0]
            context += "\n[TRUNCATED]"

    # =========================
    # PROMPT
    # =========================
    prompt = f"""
You are CyberShield AI, a cybersecurity assistant integrated into a SIEM platform.

RULE:
- Use SIEM context only if provided
- Otherwise answer as a cybersecurity expert

SIEM CONTEXT:
{context if context else "No SIEM context required."}

USER QUESTION:
{message}

RULES:
- Be concise and professional
- Use SIEM data only when present
- If data is missing, say so clearly
- No markdown, no symbols, no formatting
- Plain text only
"""

    # HARD SAFETY LIMIT (prevents Ollama crash)
    prompt = prompt[:10000]

    response = ask_ai(prompt)

    return jsonify({
        "response": response
    })