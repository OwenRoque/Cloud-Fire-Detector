# ✅ FASE 2 COMPLETADA - Fog Computing Layer

## Estado: FOG PROCESSOR LISTO PARA PROBAR (100% LOCAL, $0)

---

## 📁 Archivos Creados (6 archivos)

```
fog/
├── fog_processor.py          ⭐ ORQUESTADOR PRINCIPAL (400 líneas)
├── requirements.txt          📦 Dependencias Python
├── setup_mosquitto.sh        🦟 Instalación MQTT Broker
├── setup_fog.sh              ⚙️  Setup automático del Fog
├── README.md                 📖 Documentación completa
└── (generados en runtime:)
    ├── start_fog.sh          🚀 Script de inicio rápido
    ├── fog_config.json       🗺️  Mapa de proximidad
    ├── fog_processor.log     📋 Logs
    ├── .venv/                🐍 Virtualenv Python
    └── certs/                🔐 Certificados AWS (post-deploy)
```

---

## 🌫️ Fog Processor - Características Implementadas

### ✅ Funcionalidades Core

1. **Escucha MQTT Local**
   - Topic wildcard: `industria/+/sensor/#`
   - Procesa JSON de sensores
   - Cache de últimos datos por sensor

2. **Análisis de Riesgo**
   - Umbral de temperatura: > 60°C
   - Umbral de luz: > 800 (fuego)
   - Umbral de humedad: < 30% (seco)
   - Logging detallado por sensor

3. **Confirmación Visual**
   - Mapa de proximidad: `sensor_id` → `camera_ip`
   - HTTP POST a `http://<camera_ip>:5000/capturar`
   - Timeout: 10 segundos
   - Manejo de errores (cámara offline)

4. **Respuesta Local (MODO ISLA)**
   - ✅ Funciona **sin internet**
   - Simula acciones de extinción:
     - Cierre de válvulas de gas
     - Activación de nitrógeno
     - Sirenas de evacuación
   - Publica en `industria/alertas/local`

5. **Cooldown de Alertas**
   - 60 segundos entre alertas del mismo sensor
   - Evita duplicados

6. **Publicación a Cloud (preparado)**
   - Variable `AWS_IOT_ENABLED` (False por defecto)
   - Placeholder para AWS IoT SDK v2
   - Payload JSON compatible con Lambda

---

## 🚀 Instalación y Uso

### Paso 1: Instalar Mosquitto (Laptop B)

```bash
cd fog/
./setup_mosquitto.sh
```

**Verifica:**
```bash
sudo systemctl status mosquitto
mosquitto_sub -h localhost -t 'test' -C 1 &
mosquitto_pub -h localhost -t 'test' -m 'Hello'
```

### Paso 2: Configurar Fog Processor

```bash
./setup_fog.sh
```

Esto crea:
- Virtualenv en `.venv/`
- `fog_config.json` con configuración por defecto
- Script `start_fog.sh`

### Paso 3: Iniciar Fog Processor

```bash
./start_fog.sh
```

**Salida esperada:**
```
======================================================================
🌫️  FOG PROCESSOR - Fire Detection System
   Universidad Nacional de San Agustín - Arequipa, Perú
======================================================================

2025-12-28 10:30:00 - FogProcessor - INFO - 🌫️  Fog Processor inicializado
2025-12-28 10:30:00 - FogProcessor - INFO -    Broker MQTT: localhost:1883
2025-12-28 10:30:00 - FogProcessor - INFO -    Umbrales: {'temperatura': 60.0, 'luz': 800.0, 'humedad': 30.0}
2025-12-28 10:30:00 - FogProcessor - INFO - ✅ Conectado al broker MQTT local
2025-12-28 10:30:00 - FogProcessor - INFO - 📡 Suscrito a: industria/+/sensor/#
2025-12-28 10:30:00 - FogProcessor - INFO - ✅ Fog Processor en ejecución
2025-12-28 10:30:00 - FogProcessor - INFO -    Esperando datos de sensores...
```

---

## 🧪 Pruebas Rápidas

### Prueba 1: Alerta Normal (Temp + Luz críticas)

**En otra terminal:**
```bash
mosquitto_pub -h localhost -t 'industria/zona1/sensor/test' \
  -m '{"device_id":"sensor-zona1","temperatura":65,"luz":900,"humedad":25}'
```

**Resultado esperado:**
```
📥 Datos recibidos de sensor-zona1 (zona: zona1)
   🌡️  Temp: 65.0°C 🔥
   💡 Luz: 900 🔥
   💧 Humedad: 25.0% ⚠️
🚨 ALERTA: Posible incendio detectado en zona1
   Sensor: sensor-zona1
   Temp: 65.0°C, Luz: 900
📸 Solicitando confirmación visual a cámara: 192.168.1.105
🔌 No se pudo conectar con la cámara 192.168.1.105
======================================================================
🚨 ACTIVANDO SISTEMA DE EXTINCIÓN LOCAL 🚨
   Zona: zona1
   Sensor: sensor-zona1
   Confirmación visual: NO (por seguridad)
======================================================================

🔴 ALERTA DE INCENDIO - RESPUESTA AUTOMÁTICA 🔴
[10:32:15] Cerrando válvulas de gas en zona zona1
[10:32:15] Activando sistema de nitrógeno
[10:32:15] Enviando alerta a control local
[10:32:15] Activando sirenas de evacuación

✅ Alerta local publicada en industria/alertas/local
```

### Prueba 2: Sensor Normal (sin alertas)

```bash
mosquitto_pub -h localhost -t 'industria/zona2/sensor/arduino' \
  -m '{"device_id":"sensor-zona2","temperatura":25,"luz":200,"humedad":60}'
```

**Resultado esperado:**
```
📥 Datos recibidos de sensor-zona2 (zona: zona2)
   🌡️  Temp: 25.0°C ✅
   💡 Luz: 200 ✅
   💧 Humedad: 60.0% ✅
```

### Prueba 3: Monitorear alertas locales

```bash
mosquitto_sub -h localhost -t 'industria/alertas/local' -v
```

Deja corriendo y lanza una alerta desde otra terminal.

---

## 🗺️ Mapa de Proximidad (fog_config.json)

Archivo generado automáticamente:

```json
{
  "sensorCameraMap": {
    "sensor-zona1": "192.168.1.105",
    "sensor-zona2": "192.168.1.105",
    "sensor-virtual-1": "192.168.1.105",
    "sensor-virtual-2": "192.168.1.105",
    "sensor-virtual-3": "192.168.1.105",
    "sensor-virtual-4": "192.168.1.105",
    "sensor-virtual-5": "192.168.1.105"
  },
  "thresholds": {
    "temperature": 60.0,
    "light": 800.0,
    "humidity": 30.0
  },
  "local_mqtt_broker": "localhost",
  "local_mqtt_port": 1883,
  "iot_endpoint": "",
  "aws_region": "us-east-1"
}
```

**Para cambiar IPs:**
```bash
nano fog/fog_config.json
# Editar IPs de cámaras
# Reiniciar fog_processor
```

---

## 📊 Arquitectura Actual (Fase 2)

```
┌─────────────────────────────────────────────────────────────┐
│              LAPTOP B - FOG NODE (✅ FUNCIONAL)             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Mosquitto MQTT Broker :1883                        │   │
│  │  - Topics: industria/+/sensor/#                     │   │
│  └────────────────┬────────────────────────────────────┘   │
│                   │ MQTT                                    │
│                   ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  fog_processor.py ⭐                                 │   │
│  │  - Escucha sensores                                 │   │
│  │  - Detecta umbrales críticos                        │   │
│  │  - Solicita confirmación visual                     │   │
│  │  - Activa respuesta local (MODO ISLA)               │   │
│  │  - [TODO] Publica a AWS IoT Core                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                           │
          │ MQTT                      │ HTTP POST
          ▼                           ▼
┌─────────────────────┐    ┌──────────────────────────────┐
│  EDGE DEVICES       │    │  Cámara Termux               │
│  (🔜 Fase 3)        │    │  (🔜 Fase 3)                 │
│  - Arduino MKR      │    │  - Flask :5000               │
│  - Sensores x5      │    │  - OpenCV detección fuego    │
└─────────────────────┘    └──────────────────────────────┘
```

---

## 🎯 Próximos Pasos (Fase 3)

### Pendientes:

1. **Edge Devices (Sensores)**
   - [ ] Modificar Arduino `.ino` para MQTT local
   - [ ] Crear `sensor_virtual.py` (5 sensores simulados)
   - [ ] Probar conectividad con Fog

2. **Edge Device (Visión Artificial)**
   - [ ] Script Termux: `termux_camera_server.py`
   - [ ] Flask server en puerto 5000
   - [ ] OpenCV detección de fuego (HSV + contornos)
   - [ ] Endpoint `/capturar` con respuesta JSON

3. **Integración Local**
   - [ ] Prueba completa: Arduino → Fog → Cámara
   - [ ] Validar MODO ISLA (sin AWS)

4. **Integración Cloud (después)**
   - [ ] Habilitar AWS IoT SDK en fog_processor
   - [ ] Probar publicación a AWS IoT Core
   - [ ] Verificar Lambda → Telegram

---

## ✨ Ventajas del Diseño Actual

### ✅ Modo Isla (Funciona sin internet)
- Si AWS cae, el sistema local sigue funcionando
- Respuesta automática de extinción
- No depende de conectividad

### ✅ Desacoplamiento
- Sensores → MQTT (estándar)
- Fog → Cámara (HTTP REST)
- Fog → Cloud (MQTT TLS)

### ✅ Escalabilidad
- Mapa de proximidad en JSON (fácil de cambiar)
- Cooldown evita alertas duplicadas
- Cache de datos por sensor

### ✅ Observabilidad
- Logs detallados en consola y archivo
- Topics MQTT monitorizables
- Métricas de latencia (cámara)

---

## 🐛 Troubleshooting

### Mosquitto no arranca
```bash
sudo systemctl status mosquitto
sudo journalctl -u mosquitto -f
```

### Fog Processor no se conecta
```bash
# Verificar IP del broker
hostname -I

# Probar conexión
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test -C 1
```

### No se reciben mensajes
```bash
# Ver todos los topics
mosquitto_sub -h localhost -t '#' -v

# Verificar formato JSON
echo '{"device_id":"test","temperatura":70}' | jq .
```

---

## 💡 Comandos Útiles

### Ver logs en tiempo real
```bash
tail -f fog/fog_processor.log
```

### Monitorear tráfico MQTT
```bash
mosquitto_sub -h localhost -t 'industria/#' -v
```

### Probar alerta crítica
```bash
mosquitto_pub -h localhost -t 'industria/test/sensor/critical' \
  -m '{"device_id":"critical-test","temperatura":85,"luz":999,"humedad":10}'
```

### Ver estadísticas Mosquitto
```bash
mosquitto_sub -h localhost -t '$SYS/broker/clients/connected' -C 1
```

---

## 📋 Checklist Fase 2

- [x] Script de instalación Mosquitto
- [x] Fog Processor completo (400 líneas)
- [x] Detección de umbrales críticos
- [x] Mapa de proximidad (sensor → cámara)
- [x] Confirmación visual (HTTP request)
- [x] Respuesta local (Modo Isla)
- [x] Cooldown de alertas
- [x] Logging detallado
- [x] Setup automático
- [x] Script de inicio rápido
- [x] Documentación completa
- [ ] Integración con AWS IoT SDK (Fase 4)

---

## 🎓 ¿Listo para continuar?

**Opciones:**

**A)** Probar Fog Processor ahora (instalando Mosquitto en tu máquina)  
**B)** Continuar con Fase 3 - Edge Devices (Arduino + sensores virtuales + Termux)  
**C)** Hacer commit del código actual a Git  

**Mi recomendación:** **Opción B** - Completar Fase 3 para tener todos los componentes Edge listos, luego hacer una prueba completa local.

¿Qué prefieres? 🚀
