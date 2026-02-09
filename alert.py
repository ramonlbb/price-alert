import os
import json
import requests
from market import get_price

ALERTS_FILE = "alerts.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

REARM_PERCENT = 0.015  # 1.5% acima do preço pós-alerta


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message
    })


def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        price = get_price(symbol)

        if price is None:
            print(f"⚠️ {symbol}: sem cotação")
            continue

        target = info["target"]

        # Inicialização segura
        if "last_target" not in info:
            info["last_target"] = target
            info["reference_price"] = price
            info["alert_sent"] = False
            updated = True

        # 🔁 Target mudou → reset total
        if target != info.get("last_target"):
            if target < price:
                info["alert_sent"] = False
                info["reference_price"] = price
                info["last_target"] = target
                info.pop("rearm_price", None)
                updated = True
            continue

        # 🔄 REARM AUTOMÁTICO
        if info.get("alert_sent") and "rearm_price" in info:
            if price >= info["rearm_price"]:
                info["alert_sent"] = False
                info["reference_price"] = price
                info.pop("rearm_price", None)
                updated = True
                print(f"🔄 {symbol}: alerta rearmado automaticamente")

        # Se já alertou e ainda não rearmou, ignora
        if info.get("alert_sent"):
            continue

        print(f"{symbol}: preço {price:.2f} | alvo {target:.2f}")

        # 🟢 ALERTA DE COMPRA
        if price <= target:
            send_telegram_message(
                f"🟢 OPORTUNIDADE DE COMPRA\n\n"
                f"Ativo: {symbol}\n"
                f"Preço atual: {price:.2f}\n"
                f"Preço alvo: {target:.2f}"
            )

            info["alert_sent"] = True
            info["rearm_price"] = round(price * (1 + REARM_PERCENT), 2)
            updated = True

            print(
                f"✅ {symbol}: alertado | rearm em {info['rearm_price']:.2f}"
            )

    if updated:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    main()
