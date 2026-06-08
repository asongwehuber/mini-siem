from flask import Blueprint, request, jsonify
from app.ai.ollama_client import ask_ai

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("message", "")

    answer = ask_ai(question)

    return jsonify({
        "response": answer
    })