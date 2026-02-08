import os
import requests

TELEGRAM_TOKEN = os.getenv("8144439282:AAERv54Al04XeVVXoYGSsb80KyvB3jOPj0I")
CHAT_ID = os.getenv("957507608")

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()

if __name__ == "__main__":
    send_telegram_message("✅ Price Alert rodando corretamente no GitHub Actions.")
