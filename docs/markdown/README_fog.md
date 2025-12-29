# 🌫️ Fog Computing Layer - Fire Detection System

## Descripción

El **Fog Processor** es el orquestador central que corre en la **Laptop B** y actúa como puente entre los dispositivos Edge (sensores, cámaras) y el Cloud (AWS).

### Funcionalidades

1. **Escucha sensores locales** via MQTT (Mosquitto)
2. **Detecta umbrales críticos** (temperatura, luz, humedad)
3. **Solicita confirmación visual** a la cámara más cercana
4. **Activa respuesta local** (Modo Isla - funciona sin internet)
5. **Publica a AWS IoT Core** (solo si hay conectividad)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              LAPTOP B - FOG NODE (Este servidor)        │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Mosquitto MQTT Broker (puerto 1883)             │  │
│  │  Topic: industria/+/sensor/#                     │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                     │
│                   ▼                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  fog_processor.py (Este script)                  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ 1. Recibe datos de sensores               │  │  │
│  │  │ 2. Analiza umbrales críticos              │  │  │
│  │  │ 3. Solicita confirmación a cámara         │  │  │
│  │  │ 4. Activa respuesta local (nitrógeno)     │  │  │
│  │  │ 5. Publica a AWS IoT Core (si disponible) │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
          │                           │
          │ MQTT Local                │ HTTP
          ▼                           ▼
┌─────────────────────┐    ┌──────────────────────────┐
│  EDGE DEVICES       │    │  Cámara (Termux)         │
│  - Arduino MKR      │    │  - Flask server :5000    │
│  - Sensores (x5)    │    │  - OpenCV detección      │
└─────────────────────┘    └──────────────────────────┘
```

---

## Instalación

### Prerequisitos

- **Sistema Operativo:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.8+
- **Mosquitto MQTT Broker**
- **AWS CLI** (opcional, solo para modo Cloud)

### Paso 1: Instalar Mosquitto

```bash
./setup_mosquitto.sh
```

Esto instalará y configurará Mosquitto en el puerto 1883.

### Paso 2: Configurar Fog Processor

```bash
./setup_fog.sh
```

Esto:
- Crea un virtualenv en `.venv/`
- Instala dependencias Python
- Descarga configuración desde S3 (si está disponible)
- Crea `fog_config.json` por defecto
- Genera script de inicio `start_fog.sh`

### Paso 3: Editar Configuración (Opcional)

Edita `fog_config.json` para ajustar:

```json
{
  "sensorCameraMap": {
    "sensor-zona1": "192.168.1.105",  // Cambiar a IP real del celular
    "sensor-virtual-1": "192.168.1.105"
  },
  "thresholds": {
    "temperature": 60.0,  // Umbral de temperatura (°C)
    "light": 800.0,       // Umbral de luz (fuego)
    "humidity": 30.0      // Umbral de humedad (%)
  },
  "local_mqtt_broker": "localhost",  // O IP de esta laptop
  "local_mqtt_port": 1883
}
```

---

## Uso

### Iniciar Fog Processor

```bash
./start_fog.sh
```

O manualmente:

```bash
source .venv/bin/activate
python3 fog_processor.py
```

### Detener

Presiona `Ctrl+C`

---

## Pruebas

### 1. Probar MQTT local

En otra terminal:

```bash
# Publicar datos de sensor simulado
mosquitto_pub -h localhost -t 'industria/zona1/sensor/test' \
  -m '{"device_id":"test","temperatura":65,"luz":900,"humedad":25}'
```

**Resultado esperado:**
```
🚨 ALERTA: Posible incendio detectado en zona1
📸 Solicitando confirmación visual a cámara: 192.168.1.105
🚨 ACTIVANDO SISTEMA DE EXTINCIÓN LOCAL 🚨
```

### 2. Probar sin cámara (Modo Isla)

```bash
mosquitto_pub -h localhost -t 'industria/zona2/sensor/arduino' \
  -m '{"device_id":"sensor-zona2","temperatura":70,"luz":850,"humedad":20}'
```

Activará respuesta local aunque no haya confirmación visual.

### 3. Monitorear alertas locales

```bash
mosquitto_sub -h localhost -t 'industria/alertas/local' -v
```

---

## Mapa de Proximidad (Sensor → Cámara)

El archivo `fog_config.json` define qué cámara responde a cada sensor:

```json
{
  "sensorCameraMap": {
    "sensor-zona1": "192.168.1.105",      // Arduino → Celular
    "sensor-virtual-1": "192.168.1.105",  // Sensor virtual → Celular
    "sensor-virtual-2": "192.168.1.106"   // Otro celular
  }
}
```

**Para cambiar en proyectos reales:**
1. Editar `fog_config.json` localmente, O
2. Modificar `variables.tf` en Terraform y volver a aplicar

---

## Logs

Los logs se guardan en:
- **Consola:** Salida estándar (stdout)
- **Archivo:** `fog_processor.log`

**Ver logs en tiempo real:**
```bash
tail -f fog_processor.log
```

---

## Integración con AWS IoT Core

### Habilitar modo Cloud

1. Aplicar infraestructura Terraform:
   ```bash
   cd ..
   terraform apply
   ./extract_certs.sh
   ```

2. Editar `fog_processor.py`:
   ```python
   AWS_IOT_ENABLED = True
   ```

3. Implementar AWS IoT SDK v2 (ver TODOs en el código)

4. Reiniciar Fog Processor

---

## Troubleshooting

### Mosquitto no se conecta
```bash
sudo systemctl status mosquitto
sudo journalctl -u mosquitto -f
```

### Python dependencies error
```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Cámara no responde
- Verificar IP de cámara en `fog_config.json`
- Verificar que el servidor Flask en Termux esté corriendo
- Probar conexión: `ping 192.168.1.105`
- Probar endpoint: `curl http://192.168.1.105:5000/`

### Sin alertas
- Verificar umbrales en `fog_config.json`
- Aumentar logging: cambiar `level=logging.DEBUG` en el código
- Ver logs: `tail -f fog_processor.log`

---

## Archivos del Directorio

```
fog/
├── fog_processor.py          # Orquestador principal ⭐
├── requirements.txt          # Dependencias Python
├── setup_mosquitto.sh        # Instalación de Mosquitto
├── setup_fog.sh              # Setup automático
├── start_fog.sh              # Script de inicio rápido (generado)
├── fog_config.json           # Configuración (generado/descargado)
├── fog_processor.log         # Logs (generado en runtime)
├── .venv/                    # Virtualenv Python (generado)
└── certs/                    # Certificados AWS IoT (generados por extract_certs.sh)
    ├── certificate.pem.crt
    ├── private.pem.key
    ├── public.pem.key
    └── AmazonRootCA1.pem
```

---

## Comandos Útiles

### Monitorear todos los topics MQTT
```bash
mosquitto_sub -h localhost -t '#' -v
```

### Ver tráfico MQTT (debug)
```bash
mosquitto_sub -h localhost -t 'industria/#' -v
```

### Probar alerta manual
```bash
mosquitto_pub -h localhost -t 'industria/planta1/sensor/manual' \
  -m '{"device_id":"manual-test","temperatura":80,"luz":950,"humedad":15}'
```

### Ver estadísticas de Mosquitto
```bash
mosquitto_sub -h localhost -t '$SYS/#' -v
```

---

## Próximos Pasos

1. ✅ Fase 2 completada - Fog Processor funcionando
2. 🔜 **Fase 3:** Crear sensores virtuales (Python) en Laptop A
3. 🔜 **Fase 3:** Modificar código Arduino para MQTT local
4. 🔜 **Fase 3:** Crear servidor cámara en Termux (Flask + OpenCV)
5. 🔜 **Fase 4:** Integración completa + pruebas end-to-end

---

## Autores

Universidad Nacional de San Agustín - Arequipa, Perú  
Proyecto: Sistema de Detección de Incendios con Fog Computing
