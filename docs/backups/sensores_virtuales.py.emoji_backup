#!/usr/bin/env python3
"""
Sensores Virtuales - Fire Detection System
Universidad Nacional de San Agustín - Arequipa, Perú

Simula 5 sensores IoT que envían datos al Fog Node vía MQTT.
Útil para pruebas sin hardware físico.

Comportamiento:
- Cada sensor envía datos cada 5 segundos
- Los valores varían aleatoriamente simulando condiciones reales
- Ocasionalmente simula un incendio (valores críticos)
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import sys
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# MQTT Broker (Fog Node - Laptop B)
MQTT_BROKER = "localhost"  # Cambiar a IP de Laptop B si corres desde otra máquina
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# Configuración de sensores virtuales
SENSORES = [
    {
        "device_id": "sensor-virtual-1",
        "zona": "zona2",
        "ubicacion": "Almacén Sector A"
    },
    {
        "device_id": "sensor-virtual-2",
        "zona": "zona3",
        "ubicacion": "Sala de Máquinas"
    },
    {
        "device_id": "sensor-virtual-3",
        "zona": "zona4",
        "ubicacion": "Oficinas Piso 2"
    },
    {
        "device_id": "sensor-virtual-4",
        "zona": "zona5",
        "ubicacion": "Laboratorio"
    },
    {
        "device_id": "sensor-virtual-5",
        "zona": "zona6",
        "ubicacion": "Parking"
    }
]

# Intervalos de envío
SEND_INTERVAL = 5  # segundos

# Probabilidad de simular incendio (1% por lectura)
FIRE_PROBABILITY = 0.01

# ============================================================================
# CLASE SENSOR VIRTUAL
# ============================================================================

class SensorVirtual:
    def __init__(self, device_id, zona, ubicacion):
        self.device_id = device_id
        self.zona = zona
        self.ubicacion = ubicacion
        self.mqtt_client = None
        self.mqtt_topic = f"industria/{zona}/sensor/{device_id}"
        
        # Valores base del sensor
        self.temp_base = random.uniform(20.0, 30.0)
        self.hum_base = random.uniform(40.0, 70.0)
        self.luz_base = random.uniform(100.0, 400.0)
        
        # Estado de incendio simulado
        self.fire_mode = False
        self.fire_start_time = 0
        self.fire_duration = 0
        
    def connect_mqtt(self, client):
        """Conecta este sensor al cliente MQTT"""
        self.mqtt_client = client
        
    def generate_data(self):
        """Genera datos del sensor con variación aleatoria"""
        
        # Verificar si entramos en modo incendio
        if not self.fire_mode and random.random() < FIRE_PROBABILITY:
            self.fire_mode = True
            self.fire_start_time = time.time()
            self.fire_duration = random.uniform(15, 45)  # 15-45 segundos
            print(f"🔥 [{self.device_id}] SIMULANDO INCENDIO por {self.fire_duration:.0f}s")
        
        # Verificar si salimos de modo incendio
        if self.fire_mode:
            elapsed = time.time() - self.fire_start_time
            if elapsed > self.fire_duration:
                self.fire_mode = False
                print(f"✅ [{self.device_id}] Incendio controlado, volviendo a normal")
        
        # Generar valores según modo
        if self.fire_mode:
            # Valores críticos durante incendio
            temperatura = random.uniform(65.0, 90.0)
            humedad = random.uniform(10.0, 25.0)
            luz = random.uniform(850.0, 999.0)
        else:
            # Valores normales con variación
            temperatura = self.temp_base + random.uniform(-5.0, 5.0)
            humedad = self.hum_base + random.uniform(-10.0, 10.0)
            luz = self.luz_base + random.uniform(-50.0, 50.0)
            
            # Mantener límites realistas
            temperatura = max(15.0, min(40.0, temperatura))
            humedad = max(20.0, min(90.0, humedad))
            luz = max(50.0, min(600.0, luz))
        
        # Presión (varía poco)
        presion = 101.3 + random.uniform(-0.5, 0.5)
        
        return {
            "device_id": self.device_id,
            "temperatura": round(temperatura, 2),
            "luz": round(luz, 1),
            "humedad": round(humedad, 2),
            "presion": round(presion, 2),
            "ubicacion": self.ubicacion,
            "timestamp": datetime.utcnow().isoformat(),
            "fire_simulation": self.fire_mode
        }
    
    def send_data(self):
        """Envía datos al Fog Node vía MQTT"""
        if not self.mqtt_client:
            print(f"⚠️  [{self.device_id}] Cliente MQTT no conectado")
            return
        
        data = self.generate_data()
        payload = json.dumps(data)
        
        try:
            self.mqtt_client.publish(self.mqtt_topic, payload, qos=0)
            
            # Log con indicador visual
            status_icon = "🔥" if self.fire_mode else "✅"
            print(f"{status_icon} [{self.device_id}] T:{data['temperatura']}°C "
                  f"L:{data['luz']:.0f} H:{data['humedad']}% → {self.mqtt_topic}")
            
        except Exception as e:
            print(f"❌ [{self.device_id}] Error al enviar: {e}")

# ============================================================================
# GESTOR DE SENSORES
# ============================================================================

class SensorManager:
    def __init__(self):
        self.mqtt_client = mqtt.Client(client_id="sensores-virtuales")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        # Crear sensores virtuales
        self.sensores = []
        for config in SENSORES:
            sensor = SensorVirtual(**config)
            sensor.connect_mqtt(self.mqtt_client)
            self.sensores.append(sensor)
        
        print(f"📡 Creados {len(self.sensores)} sensores virtuales")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado al Fog Node MQTT")
            # Publicar estado de inicio
            for sensor in self.sensores:
                status_topic = f"industria/{sensor.zona}/status"
                client.publish(status_topic, 
                              f"Sensor virtual {sensor.device_id} iniciado")
        else:
            print(f"❌ Error de conexión MQTT: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"⚠️  Desconexión inesperada (rc={rc}). Reconectando...")
    
    def start(self):
        """Inicia el envío de datos de todos los sensores"""
        print(f"🚀 Conectando a Fog Node: {MQTT_BROKER}:{MQTT_PORT}")
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            self.mqtt_client.loop_start()
            
            print(f"✅ Sistema iniciado")
            print(f"   Intervalo de envío: {SEND_INTERVAL}s")
            print(f"   Probabilidad de incendio: {FIRE_PROBABILITY*100:.1f}%")
            print(f"   Topics base: industria/zona*/sensor/*")
            print()
            print("📊 Enviando datos... (Ctrl+C para detener)")
            print("─" * 80)
            
            while True:
                # Enviar datos de todos los sensores
                for sensor in self.sensores:
                    sensor.send_data()
                
                print()  # Línea en blanco entre rounds
                time.sleep(SEND_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n⚠️  Deteniendo sensores virtuales...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("👋 Sensores virtuales detenidos")
        except Exception as e:
            print(f"💥 Error crítico: {e}")
            sys.exit(1)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("📡 SENSORES VIRTUALES - Fire Detection System")
    print("   Universidad Nacional de San Agustín - Arequipa, Perú")
    print("=" * 80)
    print()
    
    # Verificar argumentos (opcional: cambiar broker)
    if len(sys.argv) > 1:
        MQTT_BROKER = sys.argv[1]
        print(f"ℹ️  Usando broker: {MQTT_BROKER}")
        print()
    
    manager = SensorManager()
    manager.start()
