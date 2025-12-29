import json
import time
import paho.mqtt.client as mqtt

from typing import Dict

from config.settings import (
    LOCAL_MQTT_BROKER,
    LOCAL_MQTT_PORT,
    LOCAL_MQTT_KEEPALIVE,
    TOPIC_SENSORES
)

from core.detection import analyze
from core.cooldown import is_in_cooldown
from camera.visual_confirmation import request_confirmation
from camera.image_manager import ImageManager
from response.local_response import activate
from cloud.aws_iot import AWSIoTClient
from datetime import datetime


class FogProcessor:
    """
    Orquestador principal del nodo Fog.
    Coordina:
      - MQTT local (sensores)
      - Detección de incendios
      - Confirmación visual
      - Respuesta local
      - Publicación a Cloud (AWS IoT)
    """

    def __init__(self, logger):
        self.logger = logger

        # MQTT local
        self.mqtt_client = mqtt.Client(client_id="fog-local-mqtt")
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect

        # Cloud
        self.aws_client = AWSIoTClient(logger)
        
        # Image Manager
        self.image_manager = ImageManager(logger)

        # Cache de sensores
        self.sensor_cache: Dict[str, Dict] = {}

        self.logger.info(" Fog Processor inicializado")
        self.logger.info(f"   MQTT local: {LOCAL_MQTT_BROKER}:{LOCAL_MQTT_PORT}")

    # ======================================================================
    # MQTT CALLBACKS
    # ======================================================================

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info(" Conectado al broker MQTT local")
            client.subscribe(TOPIC_SENSORES)
            self.logger.info(f" Suscrito a {TOPIC_SENSORES}")
        else:
            self.logger.error(f" Error de conexión MQTT (rc={rc})")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.logger.warning(" Desconexión inesperada del broker MQTT")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split("/")

            zona = topic_parts[1] if len(topic_parts) > 1 else "unknown"
            sensor_id = payload.get("device_id", f"sensor-{zona}")

            self.logger.info(f" Datos recibidos de {sensor_id} (zona {zona})")

            self.sensor_cache[sensor_id] = {
                "data": payload,
                "zona": zona,
                "timestamp": time.time()
            }

            self._process_sensor_data(sensor_id, zona, payload)

        except json.JSONDecodeError:
            self.logger.error(f" JSON inválido en topic {msg.topic}")
        except Exception as e:
            self.logger.error(f" Error procesando mensaje: {e}", exc_info=True)

    # ======================================================================
    # LÓGICA PRINCIPAL
    # ======================================================================

    def _process_sensor_data(self, sensor_id: str, zona: str, data: Dict):
        analysis = analyze(data)

        self.logger.info(
            f"    {analysis['temperatura']}°C "
            f"{'' if analysis['temp_critical'] else ''}"
        )
        self.logger.info(
            f"    {analysis['luz']} "
            f"{'' if analysis['luz_critical'] else ''}"
        )
        self.logger.info(
            f"    {analysis['humedad']}% "
            f"{'' if analysis['humedad_critical'] else ''}"
        )

        if analysis["temp_critical"] or analysis["luz_critical"]:
            self.logger.warning(f"🚨 Riesgo de incendio en zona {zona}")

            if is_in_cooldown(sensor_id):
                self.logger.info(" Sensor en cooldown, alerta ignorada")
                return

            self._handle_fire_alert(sensor_id, zona, data)

    def _handle_fire_alert(self, sensor_id: str, zona: str, data: Dict):
        try:
            result = request_confirmation(sensor_id, zona, data)

            confirmed = result.get("fire_detected", False)
            confidence = result.get("confidence", 0.0)
            image_data = result.get("image_data")

            if confirmed:
                self.logger.critical(f" INCENDIO CONFIRMADO en {zona}")
                
                # Subir imagen a S3 si está disponible
                s3_info = None
                if image_data:
                    self.logger.info(" Recibiendo imagen de la cámara...")
                    s3_info = self.image_manager.upload_to_s3(image_data, sensor_id, zona)
                
                activate(
                    self.mqtt_client,
                    self.logger,
                    sensor_id,
                    zona,
                    data,
                    confirmed=True,
                    confidence=confidence
                )

                cloud_payload = {
                    "device_id": sensor_id,
                    "zona": zona,
                    "ubicacion": f"Planta Industrial - {zona}",
                    "fuego_detectado": True,
                    "confidence": confidence,
                    "temperatura": data.get("temperatura"),
                    "luz": data.get("luz"),
                    "humedad": data.get("humedad"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Agregar información de S3 si existe
                if s3_info:
                    cloud_payload["image_s3_key"] = s3_info["s3_key"]
                    cloud_payload["image_url"] = s3_info["s3_url"]
                    self.logger.info(f" URL de imagen: {s3_info['s3_url']}")

                self.aws_client.publish_alert(cloud_payload)

            else:
                self.logger.info(" Falsa alarma según cámara")

        except Exception as e:
            self.logger.error(f" Error en confirmación visual: {e}")
            activate(
                self.mqtt_client,
                self.logger,
                sensor_id,
                zona,
                data,
                confirmed=False
            )

    # ======================================================================
    # CICLO PRINCIPAL
    # ======================================================================

    def start(self):
        self.logger.info(" Iniciando Fog Processor")

        try:
            # Cloud
            self.aws_client.connect()

            # MQTT local
            self.mqtt_client.connect(
                LOCAL_MQTT_BROKER,
                LOCAL_MQTT_PORT,
                LOCAL_MQTT_KEEPALIVE
            )
            self.mqtt_client.loop_start()

            self.logger.info(" Fog Processor en ejecución")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info(" Deteniendo Fog Processor")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        except Exception as e:
            self.logger.critical(f"💥 Error crítico: {e}", exc_info=True)
            raise
