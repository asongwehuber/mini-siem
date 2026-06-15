from app.ai.siem_context import build_siem_context
from flask import Blueprint, request, jsonify
from app.ai.ollama_client import ask_ai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/ai/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    context = build_siem_context()

    prompt = f"""
    You are an expert SOC analyst integrated into a SIEM platform.

    Current SIEM data:

    {context}

    User question:

    {message}

    Instructions:

    Instructions:
    - You have access to live SIEM statistics.
    - Use the provided SIEM data whenever possible.
    - If a statistic is present in the context, answer directly using that data.
    - If the information is not available in the context, clearly state that it is unavailable.
    - For cybersecurity concepts, answer as a SOC analyst.
    """

    response = ask_ai(prompt)

    return jsonify({
        "response": response
    })