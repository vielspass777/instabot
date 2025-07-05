from flask import Flask, request
import requests, os

app = Flask(__name__)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            message_text = messaging_event.get("message", {}).get("text")
            if sender_id and message_text:
                reply = generate_reply(message_text)
                send_message(sender_id, reply)
    return "ok", 200

def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE",
        "access_token": ACCESS_TOKEN
    }
    requests.post(url, headers=headers, json=data)

def generate_reply(msg):
    msg = msg.lower()
    if "hi" in msg or "hello" in msg:
        return "Hi! 👋 How can I help you today?"
    elif "price" in msg:
        return "Prices start from €10. Want a catalog?"
    elif "help" in msg:
        return "I'm here to help. Ask me anything."
    return "Sorry, I didn't understand. Try another question?"

if __name__ == "__main__":
    app.run(port=5000)
