import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")
BOT_NAME = os.getenv("BOT_NAME", "OlaGPT")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER")

HF_MODEL = "google/flan-t5-base"
HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

OLA_LINK = "https://wa.me/2347070333459?text=𝘏𝘪+𝙊𝙡𝙖+𝘩𝘰𝘸+𝘮𝘶𝘤𝘩+𝘤𝘢𝘯+𝘺𝘰𝘶+𝘣𝘶𝘪𝘭𝘥+𝘢𝘯+𝘈𝘐+𝘧𝘰𝘳+𝘮𝘦+𝘱𝘭𝘦𝘢𝘴𝘦_"

def ask_ai(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7
        }
    }

    try:
        r = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()

        if isinstance(data, list):
            return data[0]["generated_text"]

        return "🤖 I’m thinking… try again 😅"

    except Exception as e:
        print("HF ERROR:", e)
        return "⚠️ OlaGPT is tired 😴 Please try again later!"

@app.route("/bot", methods=["POST"])
def bot():
    incoming = request.values.get("Body", "").strip()
    sender = request.values.get("From", "").replace("whatsapp:", "")

    lower = incoming.lower()

    # 👑 Creator / Developer replies
    if any(x in lower for x in ["who created you", "who built you", "who developed you", "who modified you"]):
        return f"""🤖 *{BOT_NAME}*

Built, developed & powered by 👉 *𝗢𝗹𝗮* 🚀  
👉 {OLA_LINK}
"""

    # 🛠 Admin commands
    if incoming.startswith("/"):
        if sender.endswith(ADMIN_NUMBER):
            if incoming == "/admin":
                return "👑 Admin mode activated 🚀"
            elif incoming == "/broadcast":
                return "📢 Use dashboard to send broadcast 😉"
            else:
                return "⚙️ Unknown admin command"
        else:
            return "⛔ Admin only command"

    # 🤖 AI response
    prompt = f"You are a fun, friendly WhatsApp AI called {BOT_NAME}. Reply playfully with emojis.\nUser: {incoming}\nAI:"
    reply = ask_ai(prompt)

    return reply

@app.route("/")
def home():
    return "✅ OlaGPT is running 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
