from app.ai.ollama_client import ask_ai

response = ask_ai(
    "Explain why repeated failed login attempts may indicate a brute force attack."
)

print(response)