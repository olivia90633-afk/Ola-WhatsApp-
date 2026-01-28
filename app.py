from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "olagpt_verify"

META_TOKEN = os.getenv("META_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
HF_API_KEY = os.getenv("HF_API_KEY")

OLA_LINK = "https://wa.me/+2347070333459?text=𝘏𝘪+𝙊𝙡𝙖+𝘩𝘰𝘸+𝘮𝘶𝘤𝘩+𝘤𝘢𝘯+𝘺𝘰𝘶+𝘣𝘶𝘪𝘭𝘥+𝘢𝘯+𝘈𝘐+𝘧𝘰𝘳+𝘮𝘦+𝘱𝘭𝘦𝘢𝘴𝘦_"

# ---------- WEBHOOK ----------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid token", 403

    data = request.json

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        text = msg["text"]["body"]
        sender = msg["from"]

        reply = handle_message(text)
        send_message(sender, reply)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# ---------- MESSAGE HANDLER ----------
def handle_message(text):
    lower = text.lower()

    if "who created" in lower or "who developed" in lower:
        return f"OlaGPT 🤖\n\nBuilt, developed & powered by 👉 𝗢𝗹𝗮\n{OLA_LINK}"

    if text.startswith("/help"):
        return "🤖 OlaGPT Commands:\n/help\n/about\n/stats"

    return generate_ai_reply(text)


# ---------- AI (FREE Hugging Face) ----------
def generate_ai_reply(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": f"You are OlaGPT, friendly WhatsApp AI.\nUser: {prompt}\nOlaGPT:"
    }

    r = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers=headers,
        json=payload,
        timeout=30
    )

    return r.json()[0]["generated_text"].split("OlaGPT:")[-1].strip()


# ---------- SEND MESSAGE ----------
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }

    requests.post(url, headers=headers, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
