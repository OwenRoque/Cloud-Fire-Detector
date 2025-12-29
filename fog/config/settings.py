import os

# MQTT Local
LOCAL_MQTT_BROKER = os.getenv("FOG_MQTT_BROKER", "localhost")
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_KEEPALIVE = 60

TOPIC_SENSORES = "industria/+/sensor/#"
TOPIC_ALERTAS_LOCAL = "industria/alertas/local"
TOPIC_COMANDOS = "industria/+/comandos"

THRESHOLDS = {
    "temperatura": 60.0,
    "luz": 800.0,
    "humedad": 30.0
}

SENSOR_CAMERA_MAP = {
    "sensor-zona1": "10.7.135.194",
    "sensor-zona2": "10.7.135.194",
    "sensor-virtual-1": "10.7.135.194",
    "sensor-virtual-2": "10.7.135.194",
    "sensor-virtual-3": "10.7.135.194",
    "sensor-virtual-4": "10.7.135.194",
    "sensor-virtual-5": "10.7.135.194",
}

CAMERA_PORT = 5000
CAMERA_TIMEOUT = 10

# AWS IoT
AWS_IOT_ENABLED = True
AWS_IOT_ENDPOINT = "a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com"
AWS_IOT_TOPIC_ALERTAS = "industria/zona1/alertas"
AWS_IOT_CLIENT_ID = "fog-node-001"

AWS_CERT_PATH = "fog/certs/certificate.pem.crt"
AWS_PRIVATE_KEY_PATH = "fog/certs/private.pem.key"
AWS_ROOT_CA_PATH = "fog/certs/AmazonRootCA1.pem"

ALERT_COOLDOWN = 60
