#!/usr/bin/env python3
"""
Fog Processor - Fire Detection System
Universidad Nacional de San Agustín - Arequipa, Perú

Orquestador de Fog Computing que:
1. Escucha sensores locales vía MQTT
2. Detecta umbrales críticos (temperatura, luz)
3. Solicita confirmación visual a la cámara más cercana
4. Publica alertas confirmadas a AWS IoT Core (si hay conectividad)
5. Ejecuta respuesta local (MODO ISLA si pierde internet)

Arquitectura:
    Sensores (Edge) → MQTT Local → Fog Processor → AWS IoT Core (Cloud)
                                   ↓
                              Cámara Termux (Confirmación visual)
"""

import json
import time
import logging
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Dict, Optional
import sys
import os

# AWS IoT SDK v2
from awscrt import mqtt as mqtt_connection_builder
from awsiot import mqtt_connection_builder as iot_mqtt_builder

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# MQTT Local (Mosquitto en Laptop B)
LOCAL_MQTT_BROKER = os.getenv("FOG_MQTT_BROKER", "localhost")
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_KEEPALIVE = 60

# Topics MQTT locales
TOPIC_SENSORES = "industria/+/sensor/#"  # Wildcard para todos los sensores
TOPIC_ALERTAS_LOCAL = "industria/alertas/local"
TOPIC_COMANDOS = "industria/+/comandos"

# Umbrales de detección
THRESHOLDS = {
    "temperatura": 60.0,  # °C
    "luz": 800.0,         # Nivel de luz (indica fuego)
    "humedad": 30.0       # % (ambiente seco, riesgo de incendio)
}

# Mapa de proximidad: Sensor ID → IP de cámara
SENSOR_CAMERA_MAP = {
    "sensor-zona1": "192.168.0.41",
    "sensor-zona2": "192.168.0.41",
    "sensor-virtual-1": "192.168.0.41",
    "sensor-virtual-2": "192.168.0.41",
    "sensor-virtual-3": "192.168.0.41",
    "sensor-virtual-4": "192.168.0.41",
    "sensor-virtual-5": "192.168.0.41",
}

# Endpoints de cámaras
CAMERA_PORT = 5000
CAMERA_TIMEOUT = 10

# ============================================================================
# AWS IoT Core Configuration
# ============================================================================
AWS_IOT_ENABLED = True  # ✅ HABILITADO
AWS_IOT_ENDPOINT = "a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com"
AWS_IOT_TOPIC_ALERTAS = "industria/zona1/alertas"
AWS_IOT_CLIENT_ID = "fog-node-001"

# Rutas a certificados
AWS_CERT_PATH = "fog/certs/certificate.pem.crt"
AWS_PRIVATE_KEY_PATH = "fog/certs/private.pem.key"
AWS_ROOT_CA_PATH = "fog/certs/AmazonRootCA1.pem"

# Cooldown
ALERT_COOLDOWN = 60
last_alert_time = {}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fog_processor.log')
    ]
)
logger = logging.getLogger("FogProcessor")

# ============================================================================
# FOG PROCESSOR CLASS
# ============================================================================

class FogProcessor:
    def __init__(self):
        self.mqtt_client = mqtt.Client(client_id="fog-local-mqtt")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        self.aws_mqtt_connection = None
        self.aws_connected = False
        self.sensor_data_cache = {}
        
        logger.info("🌫️  Fog Processor inicializado")
        logger.info(f"   Broker MQTT local: {LOCAL_MQTT_BROKER}:{LOCAL_MQTT_PORT}")
        logger.info(f"   AWS IoT Endpoint: {AWS_IOT_ENDPOINT}")
        logger.info(f"   Umbrales: {THRESHOLDS}")
        logger.info(f"   Cámaras registradas: {len(SENSOR_CAMERA_MAP)}")

    # ========================================================================
    # AWS IoT Connection
    # ========================================================================
    
    def connect_aws_iot(self):
        """Conecta a AWS IoT Core usando certificados X.509"""
        if not AWS_IOT_ENABLED:
            logger.info("☁️  AWS IoT deshabilitado")
            return
        
        try:
            logger.info("☁️  Conectando a AWS IoT Core...")
            
            # Construir conexión MQTT con certificados
            self.aws_mqtt_connection = iot_mqtt_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                cert_filepath=AWS_CERT_PATH,
                pri_key_filepath=AWS_PRIVATE_KEY_PATH,
                ca_filepath=AWS_ROOT_CA_PATH,
                client_id=AWS_IOT_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30
            )
            
            # Conectar
            connect_future = self.aws_mqtt_connection.connect()
            connect_future.result()
            
            self.aws_connected = True
            logger.info("✅ Conectado a AWS IoT Core exitosamente")
            logger.info(f"   Client ID: {AWS_IOT_CLIENT_ID}")
            logger.info(f"   Endpoint: {AWS_IOT_ENDPOINT}")
            
        except Exception as e:
            logger.error(f"❌ Error al conectar a AWS IoT: {e}")
            logger.info("💾 Continuando en modo local (ISLA)")
            self.aws_connected = False

    # ========================================================================
    # MQTT Local Callbacks
    # ========================================================================
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ Conectado al broker MQTT local")
            client.subscribe(TOPIC_SENSORES)
            logger.info(f"📡 Suscrito a: {TOPIC_SENSORES}")
        else:
            logger.error(f"❌ Error de conexión MQTT: {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"⚠️  Desconexión inesperada del broker MQTT (rc={rc})")
            logger.info("🔄 Intentando reconectar...")

    def on_message(self, client, userdata, msg):
        """Procesa mensajes de sensores locales"""
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split("/")
            
            zona = topic_parts[1] if len(topic_parts) > 1 else "unknown"
            sensor_id = payload.get("device_id", f"sensor-{zona}")
            
            logger.info(f"📥 Datos recibidos de {sensor_id} (zona: {zona})")
            logger.debug(f"   Topic: {msg.topic}")
            logger.debug(f"   Payload: {payload}")
            
            self.sensor_data_cache[sensor_id] = {
                "data": payload,
                "timestamp": time.time(),
                "zona": zona
            }
            
            self.analyze_fire_risk(sensor_id, payload, zona)
            
        except json.JSONDecodeError:
            logger.error(f"❌ Error al decodificar JSON del topic {msg.topic}")
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}", exc_info=True)

    # ========================================================================
    # LÓGICA DE DETECCIÓN
    # ========================================================================
    
    def analyze_fire_risk(self, sensor_id: str, data: Dict, zona: str):
        """Analiza datos del sensor y detecta riesgo de incendio"""
        
        temperatura = data.get("temperatura", 0)
        luz = data.get("luz", 0)
        humedad = data.get("humedad", 100)
        
        temp_critical = temperatura > THRESHOLDS["temperatura"]
        luz_critical = luz > THRESHOLDS["luz"]
        humedad_critical = humedad < THRESHOLDS["humedad"]
        
        logger.info(f"   🌡️  Temp: {temperatura}°C {'🔥' if temp_critical else '✅'}")
        logger.info(f"   💡 Luz: {luz} {'🔥' if luz_critical else '✅'}")
        logger.info(f"   💧 Humedad: {humedad}% {'⚠️' if humedad_critical else '✅'}")
        
        if temp_critical or luz_critical:
            logger.warning(f"🚨 ALERTA: Posible incendio detectado en {zona}")
            logger.warning(f"   Sensor: {sensor_id}")
            logger.warning(f"   Temp: {temperatura}°C, Luz: {luz}")
            
            if self.is_in_cooldown(sensor_id):
                logger.info(f"   ⏳ En cooldown, ignorando alerta duplicada")
                return
            
            self.request_visual_confirmation(sensor_id, zona, data)
    
    def is_in_cooldown(self, sensor_id: str) -> bool:
        """Verifica si el sensor está en periodo de cooldown"""
        if sensor_id in last_alert_time:
            elapsed = time.time() - last_alert_time[sensor_id]
            return elapsed < ALERT_COOLDOWN
        return False

    # ========================================================================
    # CONFIRMACIÓN VISUAL (Cámara)
    # ========================================================================
    
    def request_visual_confirmation(self, sensor_id: str, zona: str, sensor_data: Dict):
        """Solicita confirmación visual a la cámara más cercana"""
        
        camera_ip = SENSOR_CAMERA_MAP.get(sensor_id)
        
        if not camera_ip:
            logger.warning(f"⚠️  No hay cámara asignada para {sensor_id}")
            self.activate_local_response(sensor_id, zona, sensor_data, confirmed=False)
            return
        
        logger.info(f"📸 Solicitando confirmación visual a cámara: {camera_ip}")
        
        try:
            url = f"http://{camera_ip}:{CAMERA_PORT}/capturar"
            
            response = requests.post(
                url,
                json={
                    "sensor_id": sensor_id,
                    "zona": zona,
                    "temperatura": sensor_data.get("temperatura"),
                    "luz": sensor_data.get("luz")
                },
                timeout=CAMERA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                fire_detected = result.get("fire_detected", False)
                confidence = result.get("confidence", 0.0)
                
                logger.info(f"   📷 Respuesta de cámara: fire={fire_detected}, conf={confidence:.2f}")
                
                if fire_detected:
                    logger.critical(f"🔥🔥🔥 INCENDIO CONFIRMADO en {zona} 🔥🔥🔥")
                    self.activate_local_response(sensor_id, zona, sensor_data, confirmed=True, confidence=confidence)
                    self.publish_to_cloud(sensor_id, zona, sensor_data, confidence)
                else:
                    logger.info(f"✅ Falsa alarma: No se detectó fuego en la imagen")
            else:
                logger.error(f"❌ Error de cámara: HTTP {response.status_code}")
                self.activate_local_response(sensor_id, zona, sensor_data, confirmed=False)
                
        except requests.exceptions.Timeout:
            logger.error(f"⏱️  Timeout al contactar cámara {camera_ip}")
            self.activate_local_response(sensor_id, zona, sensor_data, confirmed=False)
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 No se pudo conectar con la cámara {camera_ip}")
            self.activate_local_response(sensor_id, zona, sensor_data, confirmed=False)
        except Exception as e:
            logger.error(f"❌ Error en confirmación visual: {e}", exc_info=True)
            self.activate_local_response(sensor_id, zona, sensor_data, confirmed=False)

    # ========================================================================
    # RESPUESTA LOCAL (MODO ISLA)
    # ========================================================================
    
    def activate_local_response(self, sensor_id: str, zona: str, data: Dict, confirmed: bool, confidence: float = 0.0):
        """Activa respuesta local de emergencia"""
        
        logger.critical("=" * 70)
        logger.critical("🚨 ACTIVANDO SISTEMA DE EXTINCIÓN LOCAL 🚨")
        logger.critical(f"   Zona: {zona}")
        logger.critical(f"   Sensor: {sensor_id}")
        logger.critical(f"   Confirmación visual: {'SÍ' if confirmed else 'NO (por seguridad)'}")
        logger.critical(f"   Confianza: {confidence:.1%}" if confirmed else "")
        logger.critical("=" * 70)
        
        print("\n🔴 ALERTA DE INCENDIO - RESPUESTA AUTOMÁTICA 🔴")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cerrando válvulas de gas en zona {zona}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Activando sistema de nitrógeno")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Enviando alerta a control local")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Activando sirenas de evacuación\n")
        
        last_alert_time[sensor_id] = time.time()
        
        alert_msg = {
            "event": "fire_detected",
            "zona": zona,
            "sensor_id": sensor_id,
            "confirmed": confirmed,
            "confidence": confidence,
            "temperatura": data.get("temperatura"),
            "luz": data.get("luz"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.mqtt_client.publish(
            TOPIC_ALERTAS_LOCAL,
            json.dumps(alert_msg),
            qos=1
        )
        
        logger.info(f"✅ Alerta local publicada en {TOPIC_ALERTAS_LOCAL}")

    # ========================================================================
    # PUBLICACIÓN A CLOUD (AWS IoT Core)
    # ========================================================================
    
    def publish_to_cloud(self, sensor_id: str, zona: str, data: Dict, confidence: float):
        """Publica alerta confirmada a AWS IoT Core"""
        
        if not AWS_IOT_ENABLED or not self.aws_connected:
            logger.info("☁️  AWS IoT no disponible (modo local)")
            return
        
        logger.info("☁️  Publicando alerta a AWS IoT Core...")
        
        cloud_payload = {
            "device_id": sensor_id,
            "zona": zona,
            "fuego_detectado": True,
            "confidence": confidence,
            "temperatura": data.get("temperatura"),
            "luz": data.get("luz"),
            "humedad": data.get("humedad"),
            "ubicacion": f"Planta Industrial - {zona}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Publicar a AWS IoT Core
            self.aws_mqtt_connection.publish(
                topic=AWS_IOT_TOPIC_ALERTAS,
                payload=json.dumps(cloud_payload),
                qos=mqtt_connection_builder.QoS.AT_LEAST_ONCE
            )
            
            logger.info(f"✅ Alerta enviada a AWS IoT Core")
            logger.info(f"   Topic: {AWS_IOT_TOPIC_ALERTAS}")
            logger.debug(f"   Payload: {cloud_payload}")
            
        except Exception as e:
            logger.error(f"❌ Error al publicar a AWS: {e}")
            logger.info("💾 Alerta guardada localmente")

    # ========================================================================
    # MAIN LOOP
    # ========================================================================
    
    def start(self):
        """Inicia el Fog Processor"""
        logger.info("🚀 Iniciando Fog Processor...")
        
        try:
            # Conectar a AWS IoT
            self.connect_aws_iot()
            
            # Conectar a MQTT local
            self.mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT, LOCAL_MQTT_KEEPALIVE)
            logger.info("🔌 Conectado al broker MQTT local")
            
            self.mqtt_client.loop_start()
            
            logger.info("✅ Fog Processor en ejecución")
            logger.info("   Esperando datos de sensores...")
            logger.info("   Presiona Ctrl+C para detener")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Deteniendo Fog Processor...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
            if self.aws_mqtt_connection:
                disconnect_future = self.aws_mqtt_connection.disconnect()
                disconnect_future.result()
            
            logger.info("👋 Fog Processor detenido")
        except Exception as e:
            logger.critical(f"💥 Error crítico: {e}", exc_info=True)
            sys.exit(1)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🌫️  FOG PROCESSOR - Fire Detection System")
    print("   Universidad Nacional de San Agustín - Arequipa, Perú")
    print("=" * 70)
    print()
    
    processor = FogProcessor()
    processor.start()