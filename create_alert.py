import json
from alert import get_price, ALERTS_FILE

def normalize_alerts():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        target = info["target"]
        price = get_price(symbol)

        # cria referência se não existir
        if "reference_price" not in info:
            if target >= price:
                print(f"⚠️ {symbol}: target inválido ({target} >= {price:.2f})")
                continue

            info["reference_price"] = price
            info["alert_sent"] = False
            updated = True
            print(f"✅ Referência criada para {symbol} ({price:.2f})")

        # se o target mudou, reseta alerta
        elif info.get("alert_sent") and target != info.get("last_target", target):
            info["reference_price"] = price
            info["alert_sent"] = False
            updated = True
            print(f"🔄 Alerta resetado para {symbol}")

        info["last_target"] = target

    if updated:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)

if __name__ == "__main__":
    normalize_alerts()
