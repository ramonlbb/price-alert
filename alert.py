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


def get_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        raise Exception(f"Sem dados para {symbol}")

    return float(data["Close"].iloc[-1])


def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        price = get_price(symbol)
        target = info["target"]

        # Inicialização
        if "last_target" not in info:
            info["last_target"] = target
            info["alert_sent"] = False
            info["reference_price"] = price
            updated = True

        # 🔁 TARGET MUDOU → REARMA ALERTA
        if target != info.get("last_target"):
            info["alert_sent"] = False
            info["reference_price"] = price
            info["last_target"] = target
            updated = True
            print(f"{symbol}: novo target detectado → alerta rearmado")

        # Se já alertou, não faz nada
        if info["alert_sent"]:
            continue

        print(
            f"{symbol}: preço {price:.2f} | alvo {target:.2f}"
        )

        # 🟢 ALERTA DE COMPRA
        if price <= target:
            send_telegram_message(
                f"🟢 OPORTUNIDADE DE COMPRA\n\n"
                f"Ativo: {symbol}\n"
                f"Preço atual: {price:.2f}\n"
                f"Preço alvo: {target:.2f}"
            )

            info["alert_sent"] = True
            updated = True

    if updated:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    main()
