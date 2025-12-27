import json
import os
import urllib.request

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" # Endpoint de la API de Telegram/MODIFICAR SEGUN SEA NECESARIO
    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as response:
        response.read()

def lambda_handler(event, context):
    print("SNS Event:", json.dumps(event))

    for record in event["Records"]:
        msg = json.loads(record["Sns"]["Message"])

        text = (
            "***INCENDIO DETECTADO***\n"
            f"- Ubicación: {msg.get('location')}\n"
            f"- Dispositivo: {msg.get('device')}\n"
            f"- Confianza: {msg.get('confidence')*100:.1f}%"
        )

        send_telegram(text)

    return {"statusCode": 200}
