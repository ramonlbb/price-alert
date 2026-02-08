import os
import json
import requests
import yfinance as yf

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ALERTS_FILE = "alerts.json"


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()


import csv
import io

def get_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        raise Exception(f"Sem dados para {symbol}")

    price = data["Close"].iloc[-1]
    return float(price)



def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    for symbol, info in alerts.items():
        if info["alert_sent"]:
            continue

        price = get_price(symbol)
        target = info["target"]

        print(f"{symbol}: {price} / alvo {target}")

        if price >= target:
            send_telegram_message(
                f"🚨 ALERTA DE PREÇO\n\n"
                f"Ativo: {symbol}\n"
                f"Preço atual: {price}\n"
                f"Alvo definido: {target}"
            )

            info["alert_sent"] = True

    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    main()
