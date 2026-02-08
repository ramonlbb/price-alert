import os
import json
import requests
from market import get_price, ALERTS_FILE

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()


def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        # já alertado → ignora
        if info.get("alert_sent"):
            continue

        # ainda não normalizado → ignora
        if "reference_price" not in info:
            continue

        price = get_price(symbol)
        target = info["target"]
        reference = info["reference_price"]

        print(
            f"{symbol}: preço {price:.2f} | alvo {target:.2f} | ref {reference:.2f}"
        )

        # ALERTA DE COMPRA (queda até o alvo)
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
