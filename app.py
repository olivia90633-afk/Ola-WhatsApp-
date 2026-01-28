from flask import Flask, request
import requests
import os
import traceback

app = Flask(__name__)

# ---------------- CONFIG ----------------
VERIFY_TOKEN = "olagpt_verify"
META_TOKEN = os.getenv("META_TOKEN")        # Meta WhatsApp Permanent Token
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")  # WhatsApp Phone Number ID
HF_API_KEY = os.getenv("HF_API_KEY")        # Hugging Face API Key

# Clickable Ola link
OLA_LINK = "https://wa.me/+2347070333459?text=𝘏𝘪+𝙊𝙡𝙖+𝘩𝘰𝘸+𝘮𝘶𝘤𝘩+𝘤.𝘢.𝘯+𝘺𝘰𝘶+𝘣𝘶𝘪𝘭𝘥+𝘢𝘯+AI+for+me+please_"

# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        if request.method == "GET":
            # Meta verification
            if request.args.get("hub.verify_token") == VERIFY_TOKEN:
                return request.args.get("hub.challenge")
            return "Invalid token", 403

        data = request.json
        print("Webhook received:", data)  # log for debugging

        # Extract message
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = msg["from"]
        text = msg.get("text", {}).get("body", "")

        # Skip empty messages
        if not text:
            return "ok", 200

        # Handle message
        reply = handle_message(text.strip())

        # Send reply
        send_message(sender, reply)

    except Exception as e:
        print("Webhook error:", e)
        traceback.print_exc()

    return "ok", 200

# ---------------- MESSAGE HANDLER ----------------
def handle_message(text):
    lower = text.lower()

    # Admin commands
    if lower.startswith("/help"):
        return "🤖 OlaGPT Commands:\n/help\n/about\n/stats"
    
    if "who created" in lower or "who developed" in lower:
        return f"OlaGPT 🤖\nBuilt, developed & powered by 👉 𝗢𝗹𝗮\n{OLA_LINK}"

    if lower.startswith("/stats"):
        return "📊 Stats are not yet implemented in free version."

    # Otherwise call AI
    return generate_ai_reply(text)

# ---------------- AI RESPONSE (Hugging Face FREE) ----------------
def generate_ai_reply(prompt):
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": f"You are OlaGPT, friendly WhatsApp AI.\nUser: {prompt}\nOlaGPT:"}
        r = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers=headers,
            json=payload,
            timeout=25
        )
        output = r.json()
        # Make sure we return text safely
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].split("OlaGPT:")[-1].strip()
        return "🤖 OlaGPT is thinking… try again in a moment!"
    except Exception as e:
        print("AI error:", e)
        return "🤖 OlaGPT is temporarily unavailable. Please try again."

# ---------------- SEND WHATSAPP MESSAGE ----------------
def send_message(to, text):
    try:
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
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        print("Message sent:", r.status_code, r.text)
    except Exception as e:
        print("Send message error:", e)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
