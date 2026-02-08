def main():
    with open(ALERTS_FILE, "r") as f:
        alerts = json.load(f)

    updated = False

    for symbol, info in alerts.items():
        # se já alertou, ignora
        if info.get("alert_sent"):
            continue

        # se ainda não tem referência, ignora (create_alert resolve)
        if "reference_price" not in info:
            continue

        price = get_price(symbol)
        target = info["target"]
        reference = info["reference_price"]

        print(
            f"{symbol}: preço {price:.2f} | alvo {target:.2f} | ref {reference:.2f}"
        )

        # ALERTA DE COMPRA: preço caiu até o alvo
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
