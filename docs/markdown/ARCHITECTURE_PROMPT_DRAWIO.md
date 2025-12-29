# Prompt para Draw.io - Arquitectura Cloud Fire Detection System

Genera un diagrama de arquitectura IoT de 3 capas (Edge-Fog-Cloud) para un sistema de detección de incendios en plantas industriales:

## CAPA EDGE (Izquierda - Color Verde)

**Grupo 1: Sensores Físicos**
- Arduino MKR WiFi 1010 con MKR IoT Carrier
  - Sensores integrados: HTS221 (temp/humedad), APDS9960 (luz), LPS22HB (presión)
  - Device ID: "sensor-zona1"
  - Conectado vía WiFi (2.4GHz)
  - Protocolo: MQTT sobre TCP/IP
  
**Grupo 2: Sensores Virtuales (Python)**
- 5 sensores simulados (sensor-virtual-1 a sensor-virtual-5)
- Generan datos cada 5 segundos
- Protocolo: MQTT sobre localhost

**Grupo 3: Cámara Visual**
- Smartphone Android con Termux
- Servidor Flask (puerto 5000)
- API: termux-camera-photo
- Endpoints: /capturar, /status
- Protocolo: HTTP REST

### Conexión Edge → Fog:
- MQTT Topics: "industria/{zona}/sensor/{device_id}"
- Broker destino: Laptop (10.7.134.80:1883)
- Payload: JSON con temperatura, luz, humedad, presión

---

## CAPA FOG (Centro - Color Naranja)

**Nodo Principal: Laptop Ubuntu 24.04**

**Componente 1: Mosquitto MQTT Broker**
- Puerto: 1883
- Recibe datos de todos los sensores Edge
- Publica alertas locales

**Componente 2: Fog Processor (Python)**
- Suscrito a: "industria/+/sensor/#"
- Funciones:
  1. Análisis de umbrales (temp>60°C, luz>800)
  2. Cooldown system (60 segundos)
  3. Solicitud de confirmación visual
  4. Gestión de imágenes y S3
  5. Publicación a AWS IoT

**Componente 3: Image Manager**
- Recibe imagen en Base64 desde cámara
- Decodifica y sube a AWS S3
- Genera URL pública de imagen

**Configuración:**
- Umbrales: temperatura=60°C, luz=800, humedad=30%
- Solo "sensor-zona1" activa cámara
- AWS credentials: ~/.aws/credentials
- Certificados IoT: fog/certs/

### Conexión Fog ↔ Cámara:
- Protocolo: HTTP POST
- URL: http://192.168.1.105:5000/capturar
- Request: {sensor_id, zona, temperatura, luz}
- Response: {fire_detected, confidence, image_data (base64)}

### Conexión Fog → Cloud:
- Protocolo: MQTT sobre TLS 1.2
- Puerto: 8883
- Certificados: X.509
- Topic: "industria/zona1/alertas"

---

## CAPA CLOUD (Derecha - Color Azul)

**AWS Services:**

**1. AWS IoT Core**
- Endpoint: a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com
- Thing: "fog-node-001"
- Política: permite pub/sub en industria/*
- Recibe alertas con metadata de imagen

**2. IoT Rule**
- Query: SELECT * FROM 'industria/+/alertas'
- Action: Invoca Lambda function

**3. Lambda Function (fire_handler.py)**
- Runtime: Python 3.12
- RAM: 256 MB
- Timeout: 60s
- Procesa alertas de incendio
- Guarda en DynamoDB
- Publica en SNS

**4. DynamoDB Table**
- Nombre: fire-detections
- Partition Key: device_id
- Sort Key: timestamp
- Atributos: zona, temperatura, luz, humedad, confidence, image_url, ubicación

**5. S3 Bucket**
- Nombre: fire-detection-images-577272335685
- Estructura:
  ```
  /detections/
    /{zona}/
      /{sensor_id}/
        /YYYYMMDD_HHMMSS.jpg
  ```
- Encriptación: AES256
- Acceso: Privado (presigned URLs)

**6. SNS Topic**
- Nombre: fire-alerts
- Subscribers: Lambda (telegram.py)

**7. Lambda Telegram Bot**
- Envía notificaciones con:
  - Ubicación del incendio
  - Datos del sensor
  - Nivel de confianza
  - URL de imagen (si disponible)

---

## FLUJO DE DATOS COMPLETO

**Flujo Normal (Sin Incendio):**
```
Arduino → [MQTT] → Mosquitto → Fog Processor → Análisis
  └─> temp=26°C, luz=2 → Sin alerta
```

**Flujo de Alerta (Con Incendio):**
```
1. Arduino → [MQTT] → Mosquitto → Fog Processor
   └─> temp=26°C, luz=1841 → ¡ALERTA!

2. Fog Processor → [HTTP POST] → Cámara Termux
   └─> Request: {sensor_id, zona, temp, luz}

3. Cámara → Captura imagen → Analiza → Codifica Base64
   └─> Response: {fire_detected=true, confidence=0.85, image_data}

4. Fog Processor → Decodifica → [S3 PutObject] → AWS S3
   └─> Key: detections/zona1/sensor-zona1/20251229_123604.jpg

5. Fog Processor → [MQTT/TLS] → AWS IoT Core
   └─> Payload: {device_id, zona, fuego_detectado, image_url, ...}

6. IoT Core → [IoT Rule] → Lambda (fire_handler)
   └─> Procesa alerta

7. Lambda → [SDK] → DynamoDB
   └─> Guarda registro histórico

8. Lambda → [SNS Publish] → SNS Topic
   └─> fire-alerts

9. SNS → [Event] → Lambda (telegram.py)
   └─> Envía mensaje a Telegram

10. Usuario → Recibe notificación con imagen
```

---

## ELEMENTOS VISUALES ADICIONALES

**Iconos sugeridos:**
- Edge: Microcontrolador, smartphone, sensor
- Fog: Laptop, server
- Cloud: AWS logo, database, storage, notification

**Colores:**
- Edge: Verde (#4CAF50)
- Fog: Naranja (#FF9800)
- Cloud: Azul (#2196F3)
- Conexiones MQTT: Púrpura
- Conexiones HTTP: Azul claro
- Alertas: Rojo

**Leyendas:**
- MQTT (no seguro): Línea punteada
- MQTT/TLS: Línea sólida con candado
- HTTP: Línea delgada
- Flujo de datos críticos: Línea gruesa roja

**Notas en el diagrama:**
1. "WiFi 2.4GHz - Red: wifi-CsComputacion"
2. "Cooldown: 60s para evitar spam"
3. "Solo sensor-zona1 activa cámara"
4. "Imagen en Base64 (300-700 KB)"
5. "Región AWS: us-east-1"
