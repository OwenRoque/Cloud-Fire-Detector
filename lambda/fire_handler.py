import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

sns = boto3.client("sns")
dynamodb = boto3.resource("dynamodb")

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
TABLE_NAME = os.environ.get("TABLE_NAME", "fire-events")

def convert_floats(obj):
    """Convierte recursivamente floats a Decimal para DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats(v) for v in obj]
    return obj

def lambda_handler(event, context):
    print(" Evento recibido:", json.dumps(event, default=str))

    try:
        # Detectar origen (IoT o API Gateway)
        if "body" in event:
            payload = json.loads(event["body"])
        else:
            payload = event

        # Validar campos requeridos
        required = ["device_id", "fuego_detectado", "confidence"]
        for r in required:
            if r not in payload:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Missing field: {r}"})
                }

        # Si no hay fuego, salir temprano
        if not payload["fuego_detectado"]:
            print("ℹ️  No fire detected, skipping alert")
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "no_fire"})
            }

        # Construir item para DynamoDB
        item = {
            "event_id": f'{payload["device_id"]}-{int(datetime.utcnow().timestamp())}',
            "device_id": payload["device_id"],
            "confidence": payload["confidence"],
            "temperature": payload.get("temperatura", -1),
            "location": payload.get("ubicacion", "unknown"),
            "zona": payload.get("zona", "unknown"),
            "luz": payload.get("luz", 0),
            "humedad": payload.get("humedad", 0),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat())
        }

        # Convertir todos los floats a Decimal recursivamente
        item = convert_floats(item)

        # Guardar en DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=item)
        print(f" Evento guardado en DynamoDB: {item['event_id']}")

        # Publicar alerta a SNS
        message = {
            "alert": " INCENDIO DETECTADO",
            "device": payload["device_id"],
            "zona": payload.get("zona", "unknown"),
            "confidence": float(payload["confidence"]),  # SNS puede recibir float
            "temperature": payload.get("temperatura", -1),
            "location": payload.get("ubicacion", "unknown"),
            "timestamp": payload.get("timestamp")
        }

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message, indent=2, default=str),
            Subject="🚨 Fire Alert - Incendio Detectado"
        )
        print(f" Alerta publicada a SNS: {SNS_TOPIC_ARN}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "event_id": str(item["event_id"]),
                "message": "Fire event processed successfully"
            })
        }

    except Exception as e:
        print(f" Error procesando evento: {str(e)}")
        print(f"   Payload: {json.dumps(payload, default=str)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "event": event
            })
        }