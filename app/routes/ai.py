from flask import Blueprint, request, jsonify
from app.database.models import Alert
from app.ai.ollama_client import ask_ai

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/alert/<int:alert_id>/explain")
def explain_alert(alert_id):

    alert = Alert.query.get_or_404(alert_id)

    prompt = f"""
    You are a cybersecurity analyst.

    Analyze this SIEM alert.

    Alert Name: {alert.alert_name}
    Severity: {alert.severity}
    Source IP: {alert.source_ip}
    Event Count: {alert.event_count}
    Status: {alert.status}
    Description: {alert.description}

    Explain:
    1. What this alert means
    2. Why it may have been triggered
    3. Potential security risks
    4. Recommended investigation steps
    5. Recommended mitigation actions

    Keep the explanation concise and practical.
    """

    explanation = ask_ai(prompt)

    return jsonify({
        "alert_id": alert.id,
        "alert_name": alert.alert_name,
        "explanation": explanation
    })



@ai_bp.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("message", "")

    response = ask_ai(question)

    return jsonify({
        "response": response
    })