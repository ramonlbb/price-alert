import os
import json
import requests
import base64

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GH_TOKEN = os.getenv("GH_TOKEN")

REPO = "ramonlbb/price-alert"
BRANCH = "main"

ALERTS_FILE = "alerts.json"
OFFSET_FILE = "telegram_offset.json"


def gh_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }


def gh_get_file(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    r = requests.get(url, headers=gh_headers())
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode()
    return json.loads(content), data["sha"]


def gh_update_file(path, content_json, sha, message):
    content = base64.b64encode(
        json.dumps(content_json, indent=2).encode()
    ).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": content,
        "sha": sha,
        "branch": BRANCH
    }

    r = requests.put(url, headers=gh_headers(), json=payload)
    r.raise_for_status()


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})


def process_command(text):
    parts = text.split()

    if parts[0] == "/alert" and len(parts) == 3:
        symbol = parts[1].upper() + ".SA"
        target = float(parts[2])

        alerts, sha = gh_get_file(ALERTS_FILE)

        alerts[symbol] = {
            "target": target,
            "alert_sent": False
        }

        gh_update_file(
            ALERTS_FILE,
            alerts,
            sha,
            f"Atualiza alerta {symbol} {target}"
        )

        send_message(f"✅ Alerta atualizado\n{symbol}\nPreço alvo: {target}")

    elif parts[0] == "/list":
        alerts, _ = gh_get_file(ALERTS_FILE)

        if not alerts:
            send_message("Nenhum alerta ativo.")
            return

        msg = "📊 Alertas ativos:\n\n"
        for s, i in alerts.items():
            msg += f"{s} → {i['target']}\n"

        send_message(msg)

    else:
        send_message(
            "Comandos:\n"
            "/alert ATIVO PRECO\n"
            "/list"
        )


def main():
    offset_data, offset_sha = gh_get_file(OFFSET_FILE)
    last_update = offset_data.get("last_update_id", 0)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"offset": last_update + 1}
    r = requests.get(url, params=params).json()

    if not r["result"]:
        return

    for upd in r["result"]:
        update_id = upd["update_id"]
        msg = upd.get("message")
        if not msg:
            continue

        chat_id = str(msg["chat"]["id"])
        if chat_id != CHAT_ID:
            continue

        text = msg["text"]
        process_command(text)

        offset_data["last_update_id"] = update_id
        gh_update_file(
            OFFSET_FILE,
            offset_data,
            offset_sha,
            "Atualiza offset Telegram"
        )


if __name__ == "__main__":
    main()
