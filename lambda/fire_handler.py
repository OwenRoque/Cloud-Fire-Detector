import json
import os
import boto3
from datetime import datetime

sns = boto3.client("sns")
dynamodb = boto3.resource("dynamodb")

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
TABLE_NAME = os.environ.get("TABLE_NAME", "fire-events")

def lambda_handler(event, context):
    print("🔥 Evento recibido:", json.dumps(event))

    # Detectar origen (IoT o API Gateway)
    if "body" in event:
        payload = json.loads(event["body"])
    else:
        payload = event

    required = ["device_id", "fuego_detectado", "confidence"]
    for r in required:
        if r not in payload:
            return {
                "statusCode": 400,
                "body": f"Missing field: {r}"
            }

    if not payload["fuego_detectado"]:
        return {
            "statusCode": 200,
            "body": "No fire detected"
        }

    item = {
        "event_id": f'{payload["device_id"]}-{int(datetime.utcnow().timestamp())}',
        "device_id": payload["device_id"],
        "confidence": float(payload["confidence"]),
        "temperature": payload.get("temperatura", -1),
        "location": payload.get("ubicacion", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Guardar en DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item=item)

    # Publicar alerta
    message = {
        "alert": "INCENDIO DETECTADO",
        "device": payload["device_id"],
        "confidence": payload["confidence"],
        "location": payload.get("ubicacion", "unknown")
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        Subject="Fire Alert"
    )

    return {
        "statusCode": 200,
        "body": "Fire event processed"
    }
