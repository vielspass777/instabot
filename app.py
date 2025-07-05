from flask import Flask, request
import requests, os

app = Flask(__name__)

# Access your environment variables securely
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# Facebook webhook verification endpoint
@app.route("/", methods=["GET"])
def verify():
    # Meta sends hub.challenge to verify webhook
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token"

# Main webhook listener for messages
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    
    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            message_text = messaging_event.get("message", {}).get("text")

            # Basic check to avoid empty messages or errors
            if sender_id and message_text:
                reply = generate_reply(message_text)
                send_message(sender_id, reply)
    
    return "ok", 200

# Function to send a message back to the user
def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE",
        "access_token": ACCESS_TOKEN
    }
    requests.post(url, headers=headers, json=data)

# Simple logic to return different responses based on user input
def generate_reply(msg):
    msg = msg.lower()
    if "hi" in msg or "hello" in msg:
        return "Hi! 👋 How can I help you today?"
    elif "price" in msg:
        return "Prices start from €10. Want a catalog?"
    elif "help" in msg:
        return "I'm here to help. Ask me anything."
    else:
        return "Sorry, I didn't understand. Try another question?"

# ✅ Crucial fix: listen on all interfaces, not just 127.0.0.1
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
