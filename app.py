from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

META_TOKEN = os.getenv("META_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

PREDEFINED_RESPONSES = {
    "hello": "👋 Hey there! How's your day going? 😎✨",
    "who created you": "🤖 I'm built, developed & powered by 👉 𝗢𝗹𝗮\nhttps://wa.me/+2347070333459?text=Hi+Ola",
    "/help": "📚 Commands available:\n- /help\n- /stats\n- /admin",
    "default": "🤖 OlaGPT says: Sorry, I don't understand that yet 😅"
}

def send_whatsapp(to_number, message):
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "text": {"body": message}
    }
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, json=payload, headers=headers)
    print("Message sent:", r.status_code, r.text)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        # Meta verification
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == "olagpt_verify":
            return challenge
        return "Invalid token", 403

    # POST - handle messages
    data = request.json
    print("Webhook received:", data)

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        text = msg["text"]["body"].lower()

        # Pick predefined response
        response = PREDEFINED_RESPONSES.get(text, PREDEFINED_RESPONSES["default"])

        send_whatsapp(from_number, response)
    except Exception as e:
        print("Error handling message:", e)

    return jsonify(status=200)
