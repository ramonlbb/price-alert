import os
import json
import requests
import base64

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GH_TOKEN = os.getenv("GH_TOKEN")

REPO = "ramonlbb/price-alert"
FILE_PATH = "alerts.json"
BRANCH = "main"


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})


def github_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }


def get_alerts():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=github_headers())
    r.raise_for_status()
    data = r.json()

    content = base64.b64decode(data["content"]).decode()
    return json.loads(content), data["sha"]


def update_alerts(alerts, sha, message):
    content = base64.b64encode(
        json.dumps(alerts, indent=2).encode()
    ).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    payload = {
        "message": message,
        "content": content,
        "sha": sha,
        "branch": BRANCH
    }

    r = requests.put(url, headers=github_headers(), json=payload)
    r.raise_for_status()


def process_command(text):
    parts = text.split()

    if parts[0] == "/alert" and len(parts) == 3:
        symbol = parts[1].upper() + ".SA"
        target = float(parts[2])

        alerts, sha = get_alerts()

        alerts[symbol] = {
            "target": target,
            "alert_sent": False
        }

        update_alerts(alerts, sha, f"Novo alerta {symbol} {target}")
        send_message(f"✅ Alerta criado\n{symbol}\nPreço alvo: {target}")

    elif parts[0] == "/remove" and len(parts) == 2:
        symbol = parts[1].upper() + ".SA"

        alerts, sha = get_alerts()

        if symbol in alerts:
            del alerts[symbol]
            update_alerts(alerts, sha, f"Remove alerta {symbol}")
            send_message(f"🗑️ Alerta removido: {symbol}")
        else:
            send_message("⚠️ Ativo não encontrado")

    elif parts[0] == "/list":
        alerts, _ = get_alerts()

        if not alerts:
            send_message("Nenhum alerta ativo.")
            return

        msg = "📊 Alertas ativos:\n\n"
        for s, i in alerts.items():
            msg += f"{s} → {i['target']}\n"

        send_message(msg)

    else:
        send_message(
            "❓ Comandos disponíveis:\n"
            "/alert ATIVO PRECO\n"
            "/remove ATIVO\n"
            "/list"
        )


def main():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    r = requests.get(url).json()

    if not r["result"]:
        return

    last = r["result"][-1]
    chat_id = str(last["message"]["chat"]["id"])

    if chat_id != CHAT_ID:
        return

    text = last["message"]["text"]
    process_command(text)


if __name__ == "__main__":
    main()
