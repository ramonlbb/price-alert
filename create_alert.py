import json
from market import get_price, ALERTS_FILE


def normalize_alerts():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        target = info["target"]
        price = get_price(symbol)

        # 🔴 sem preço → ignora ativo
        if price is None:
            print(f"⚠️ {symbol}: sem cotação no momento (ignorado)")
            continue

        # 🟡 cria referência automaticamente
        if "reference_price" not in info:
            if target >= price:
                print(
                    f"⚠️ {symbol}: target {target:.2f} >= preço atual {price:.2f} (ignorado)"
                )
                continue

            info["reference_price"] = price
            info["alert_sent"] = False
            info["last_target"] = target
            updated = True

            print(f"✅ Referência criada para {symbol}: {price:.2f}")
            continue

        # 🔁 target mudou → reseta alerta
        if info.get("last_target") != target:
            if target >= price:
                print(
                    f"⚠️ {symbol}: novo target inválido ({target:.2f} >= {price:.2f})"
                )
                continue

            info["reference_price"] = price
            info["alert_sent"] = False
            info["last_target"] = target
            updated = True

            print(f"🔄 Alerta resetado para {symbol}")

    if updated:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    normalize_alerts()
