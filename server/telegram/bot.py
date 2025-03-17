import requests

users = [6187338627, 1204722136]
url = f""

def send_telegram_message(message):
    for user in users:
        params = {
            "chat_id": user,
            "text": message
        }
        requests.get(url, params=params)

def notify_pump(symbol, direction, pump_text):
    message = f"🚨 {symbol} - {direction} 🚨\n{pump_text}"
    send_telegram_message(message)