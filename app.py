import requests
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from feedback import send_feedback
from pathlib import Path

# Load environment variables explicitly from your .env file once
load_dotenv(dotenv_path=Path('.env'))

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Serve the HTML
@app.route("/")
def home():
    return render_template("index.html")

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        output = response.json()
        ai_reply = output["choices"][0]["message"]["content"]
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Feedback endpoint
@app.route("/feedback", methods=["POST"])
def feedback():
    print(f"DEBUG: FEEDBACK_EMAIL loaded as: {os.getenv('FEEDBACK_EMAIL')}")
    print(f"DEBUG: YOUR_PASSWORD loaded as: {os.getenv('YOUR_PASSWORD')}")

    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    if send_feedback(name, email, message):
        return jsonify({"success": True, "message": "Feedback sent successfully"})
    else:
        return jsonify({"success": False, "error": "Failed to send feedback"}), 500


if __name__ == "__main__":
    # Create the 'static' and 'templates' folders if they don't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # For deployment platforms like Railway, use PORT env var, else default 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
