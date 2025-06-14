import os
import requests

def send_telegram_message(message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials not found in environment.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("Failed to send Telegram message:", response.text)