import requests
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Serve your HTML file
@app.route("/")
def home():
    return render_template("index.html")

# Handle chat requests
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4o-mini",
        "input": user_input,
        "store": False
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        output = response.json()
        ai_reply = output["output"][0]["content"][0]["text"]
        return jsonify({"reply": ai_reply})
    else:
        return jsonify({"error": response.text})

if __name__ == "__main__":
    app.run(debug=True)
