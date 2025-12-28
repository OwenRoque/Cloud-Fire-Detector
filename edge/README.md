# 📡 Edge Computing Layer - Fire Detection System

## Descripción

Los **Edge Devices** son los sensores y cámaras distribuidas que recopilan datos ambientales y confirman visualmente los incendios.

### Componentes

1. **Arduino MKR WiFi 1010** - Sensor físico con MKR IoT Carrier
2. **Sensores Virtuales** - 5 sensores simulados en Python
3. **Cámara Termux** - Servidor Flask + OpenCV en Android

---

## 1️⃣ Arduino MKR WiFi 1010

### Hardware Requerido
- Arduino MKR WiFi 1010
- Arduino MKR IoT Carrier (Rev2)
- Cable USB

### Instalación

1. **Instalar Arduino CLI** (si no está instalado):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
   ```

2. **Instalar librerías necesarias**:
   ```bash
   arduino-cli lib install "WiFiNINA"
   arduino-cli lib install "ArduinoMqttClient"
   arduino-cli lib install "ArduinoJson"
   arduino-cli lib install "Arduino_MKRIoTCarrier"
   ```

3. **Compilar el sketch**:
   ```bash
   arduino-cli compile --fqbn arduino:samd:mkrwifi1010 fire_detection_fog_mqtt.ino
   ```

4. **Subir al Arduino**:
   ```bash
   arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:samd:mkrwifi1010 fire_detection_fog_mqtt.ino
   ```

### Configuración

Editar en el archivo `.ino`:

```cpp
const char* ssid = "TU_WIFI_SSID";           // Tu red WiFi
const char* password = "TU_WIFI_PASSWORD";   // Tu contraseña
const char* mqtt_broker = "192.168.1.100";  // IP de Laptop B (Fog Node)
const char* device_id = "sensor-zona1";      // ID único del sensor
```

### Topics MQTT

- **Publica en:** `industria/zona1/sensor/arduino`
- **Se suscribe a:** `industria/zona1/comandos`

### Payload JSON

```json
{
  "device_id": "sensor-zona1",
  "temperatura": 25.5,
  "luz": 350.2,
  "humedad": 55.8,
  "presion": 101.3,
  "timestamp": 12345
}
```

---

## 2️⃣ Sensores Virtuales (Python)

### Descripción

Simula 5 sensores IoT sin necesidad de hardware físico.

### Instalación

```bash
pip install paho-mqtt
```

### Uso

**Desde Laptop A (o cualquier máquina en la red):**

```bash
# Si corres en la misma máquina que el Fog:
python3 sensores_virtuales.py

# Si corres desde otra máquina:
python3 sensores_virtuales.py 192.168.1.100
```

### Sensores Simulados

| Device ID | Zona | Ubicación |
|-----------|------|-----------|
| `sensor-virtual-1` | zona2 | Almacén Sector A |
| `sensor-virtual-2` | zona3 | Sala de Máquinas |
| `sensor-virtual-3` | zona4 | Oficinas Piso 2 |
| `sensor-virtual-4` | zona5 | Laboratorio |
| `sensor-virtual-5` | zona6 | Parking |

### Características

- Envío cada 5 segundos
- Valores varían aleatoriamente
- **1% de probabilidad de simular incendio** por lectura
- Modo incendio dura 15-45 segundos
- Topics: `industria/zona*/sensor/sensor-virtual-*`

### Salida de Ejemplo

```
✅ [sensor-virtual-1] T:25.3°C L:350 H:55.2% → industria/zona2/sensor/sensor-virtual-1
🔥 [sensor-virtual-2] SIMULANDO INCENDIO por 30s
🔥 [sensor-virtual-2] T:75.5°C L:920 H:15.5% → industria/zona3/sensor/sensor-virtual-2
```

---

## 3️⃣ Cámara Termux (Android)

### Hardware Requerido
- Teléfono Android con cámara
- Misma red WiFi que el Fog Node

### Instalación en Termux

1. **Instalar Termux** (desde F-Droid, NO desde Play Store):
   ```
   https://f-droid.org/en/packages/com.termux/
   ```

2. **Instalar Termux:API**:
   ```
   https://f-droid.org/en/packages/com.termux.api/
   ```

3. **Dar permisos de cámara**:
   - Configuración Android → Apps → Termux:API → Permisos → Cámara ✓

4. **Instalar dependencias en Termux**:
   ```bash
   pkg update && pkg upgrade
   pkg install python opencv termux-api
   pip install flask pillow numpy opencv-python
   ```

5. **Transferir script al teléfono**:
   ```bash
   # Desde PC (usando adb o compartir archivo)
   # O copiar manualmente el código
   
   # En Termux:
   nano termux_camera_server.py
   # (Pegar el código)
   ```

6. **Iniciar servidor**:
   ```bash
   python3 termux_camera_server.py
   ```

### Endpoints

- **`GET /`** - Status del servidor
- **`GET /status`** - Estado y estadísticas
- **`POST /capturar`** - Captura foto y detecta fuego
- **`GET /test`** - Prueba sin captura real

### Ejemplo de Request

```bash
curl -X POST http://192.168.1.105:5000/capturar \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor-zona1",
    "zona": "zona1",
    "temperatura": 65,
    "luz": 900
  }'
```

### Response

```json
{
  "fire_detected": true,
  "confidence": 0.85,
  "timestamp": "2025-12-28T10:30:00",
  "image_path": "/data/data/com.termux/files/home/fire_detection_images/capture_20251228_103000.jpg",
  "sensor_id": "sensor-zona1",
  "zona": "zona1",
  "camera_id": 0
}
```

### Algoritmo de Detección

1. **Captura foto** con `termux-camera-photo`
2. **Convierte a HSV** (Hue, Saturation, Value)
3. **Máscara de color** naranja-amarillo-rojo (fuego):
   - Hue: 10-35°
   - Saturation: 100-255
   - Value: 100-255
4. **Morfología** para reducir ruido
5. **Contornos** con área > 500 píxeles
6. **Confianza** basada en % de área de fuego

---

## 🧪 Pruebas

### Prueba 1: Arduino → Fog

```bash
# En Laptop B (Fog):
mosquitto_sub -h localhost -t 'industria/zona1/sensor/#' -v

# Arduino debe enviar datos automáticamente cada 5s
```

### Prueba 2: Sensores Virtuales → Fog

```bash
# Terminal 1 (Fog):
mosquitto_sub -h localhost -t 'industria/#' -v

# Terminal 2:
python3 sensores_virtuales.py
```

### Prueba 3: Cámara (desde PC)

```bash
# Probar status
curl http://192.168.1.105:5000/status

# Probar detección
curl -X POST http://192.168.1.105:5000/capturar \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"test"}'
```

### Prueba 4: Integración Completa

```bash
# Terminal 1: Fog Processor
cd fog/
./start_fog.sh

# Terminal 2: Sensores Virtuales
cd edge/
python3 sensores_virtuales.py

# Terminal 3: Arduino (conectar y monitorear Serial)
arduino-cli monitor -p /dev/ttyACM0

# Teléfono: Iniciar servidor cámara
python3 termux_camera_server.py
```

**Esperar a que un sensor virtual simule incendio (1% de probabilidad)**

---

## 📊 Arquitectura Edge

```
┌────────────────────────────────────────────────────────┐
│                    EDGE DEVICES                        │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Arduino MKR WiFi 1010 + IoT Carrier           │  │
│  │  - Topic: industria/zona1/sensor/arduino       │  │
│  │  - Device ID: sensor-zona1                     │  │
│  └───────────────────┬─────────────────────────────┘  │
│                      │ MQTT                            │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Sensores Virtuales (Python)                   │  │
│  │  - 5 sensores simulados                        │  │
│  │  - Topics: industria/zona2-6/sensor/*          │  │
│  └───────────────────┬─────────────────────────────┘  │
│                      │ MQTT                            │
│                      ▼                                 │
│             ┌─────────────────┐                        │
│             │  FOG NODE       │                        │
│             │  (Laptop B)     │                        │
│             └────────┬────────┘                        │
│                      │ HTTP POST                       │
│                      ▼                                 │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Celular Android (Termux)                      │  │
│  │  - Flask Server :5000                          │  │
│  │  - OpenCV detección fuego                      │  │
│  │  - Endpoint: /capturar                         │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Arduino no se conecta al WiFi
- Verificar SSID y contraseña
- Asegurarse de que es red 2.4GHz (no 5GHz)
- Revisar Serial Monitor para errores

### Arduino no se conecta al MQTT
- Ping a IP del Fog Node: `ping 192.168.1.100`
- Verificar que Mosquitto está corriendo: `sudo systemctl status mosquitto`
- Verificar firewall en Laptop B

### Sensores virtuales no envían datos
- Verificar IP del broker
- Comprobar conectividad: `telnet 192.168.1.100 1883`

### Cámara Termux no responde
- Verificar permisos de cámara en Termux:API
- Probar captura manual: `termux-camera-photo test.jpg`
- Ver logs del servidor Flask

### Detección de fuego incorrecta
- Ajustar umbrales HSV en `termux_camera_server.py`
- Ajustar `MIN_FIRE_AREA`
- Probar con imágenes reales de fuego

---

## 📁 Archivos del Directorio

```
edge/
├── fire_detection_fog_mqtt.ino   # Arduino (modificado para MQTT local)
├── sensores_virtuales.py         # 5 sensores simulados
├── termux_camera_server.py       # Servidor Flask + OpenCV
├── requirements.txt               # Dependencias Python
└── README.md                      # Esta documentación
```

---

## 🎯 Próximos Pasos

- [x] Código Arduino migrado a MQTT local
- [x] Sensores virtuales funcionando
- [x] Servidor cámara con OpenCV
- [ ] Pruebas integradas con Fog
- [ ] Ajuste fino de umbrales de detección
- [ ] Deploy completo end-to-end

---

## Autores

Universidad Nacional de San Agustín - Arequipa, Perú  
Proyecto: Sistema de Detección de Incendios con Fog Computing
