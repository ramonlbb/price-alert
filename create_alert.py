import json
import os
from alert import get_price, ALERTS_FILE

def create_alert(symbol: str, target: float):
    price = get_price(symbol)

    if target >= price:
        raise Exception(
            f"Target {target} não é menor que o preço atual {price:.2f}"
        )

    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    alerts[symbol] = {
        "target": target,
        "reference_price": price,
        "alert_sent": False
    }

    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

    print(
        f"Alerta criado para {symbol}\n"
        f"Preço atual: {price:.2f}\n"
        f"Target: {target:.2f}"
    )

if __name__ == "__main__":
    import sys
    create_alert(sys.argv[1], float(sys.argv[2]))
