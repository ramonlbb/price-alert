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


def format_price_br(value: float) -> str:
    """
    Converte:
    68997.74 -> 68.997,74
    """
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        price = get_price(symbol)

        # 🔴 sem preço → ignora ativo
        if price is None:
            print(f"⚠️ {symbol}: sem cotação no momento")
            continue

        target = info["target"]

        # 🟡 inicialização defensiva
        if "last_target" not in info:
            info["last_target"] = target
            info["alert_sent"] = False
            info["reference_price"] = price
            updated = True

        # 🔁 target mudou → rearma alerta
        if target != info.get("last_target"):
            if target < price:
                info["alert_sent"] = False
                info["reference_price"] = price
                info["last_target"] = target
                updated = True
                print(f"{symbol}: novo target detectado → alerta rearmado")
            else:
                print(
                    f"⚠️ {symbol}: target inválido ({target:.2f} >= {price:.2f})"
                )
                continue

        # se já alertou, não faz nada
        if info.get("alert_sent"):
            continue

        print(
            f"{symbol}: preço {price:.2f} | alvo {target:.2f}"
        )

        # 🟢 ALERTA DE COMPRA
        if price <= target:

            # 💱 prefixo correto
            if symbol == "BTC-USD":
                price_txt = f"US$ {format_price_br(price)}"
                target_txt = f"US$ {format_price_br(target)}"
            else:
                price_txt = f"R$ {format_price_br(price)}"
                target_txt = f"R$ {format_price_br(target)}"

            send_telegram_message(
                f"🟢 OPORTUNIDADE DE COMPRA\n\n"
                f"Ativo: {symbol}\n"
                f"Preço atual: {price_txt}\n"
                f"Preço alvo: {target_txt}"
            )

            info["alert_sent"] = True
            updated = True

    if updated:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    main()
