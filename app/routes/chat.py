from flask import Blueprint, request, jsonify
from app.ai.ollama_client import ask_ai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/ai/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    prompt = f"""
    You are a SOC (Security Operations Center) analyst AI.

    User question:
    {message}

    Respond clearly and technically.
    """

    response = ask_ai(prompt)

    return jsonify({
        "response": response
    })