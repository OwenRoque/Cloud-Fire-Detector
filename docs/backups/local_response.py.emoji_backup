import json
from datetime import datetime
from config.settings import TOPIC_ALERTAS_LOCAL
from core.cooldown import update_cooldown

def activate(mqtt_client, logger, sensor_id, zona, data, confirmed, confidence=0.0):
    logger.critical("🚨 ACTIVANDO RESPUESTA LOCAL")

    update_cooldown(sensor_id)

    alert = {
        "event": "fire_detected",
        "zona": zona,
        "sensor_id": sensor_id,
        "confirmed": confirmed,
        "confidence": confidence,
        "temperatura": data.get("temperatura"),
        "luz": data.get("luz"),
        "timestamp": datetime.utcnow().isoformat()
    }

    mqtt_client.publish(TOPIC_ALERTAS_LOCAL, json.dumps(alert), qos=1)
