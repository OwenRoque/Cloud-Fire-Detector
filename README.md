# 🔥 Cloud Fire Detector - Guía de Replicación

> Sistema de detección de incendios con arquitectura Edge-Fog-Cloud  
> Universidad Nacional de San Agustín - Arequipa, Perú

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración del Sistema](#configuración-del-sistema)
4. [Ejecución del Sistema](#ejecución-del-sistema)
5. [Dashboard de Monitoreo](#dashboard-de-monitoreo)
6. [Integración con AWS (Opcional)](#integración-con-aws-opcional)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Arquitectura del Sistema

```
┌─────────────────┐
│  Edge Layer     │  Sensores IoT + Cámara
│  - Sensores     │  (Arduino MKR WiFi 1010 / Virtuales)
│  - Cámara       │  (Termux en Android)
└────────┬────────┘
         │ MQTT (puerto 1883)
         ↓
┌─────────────────┐
│  Fog Layer      │  Procesamiento Local
│  - Mosquitto    │  Broker MQTT
│  - Processor    │  Detección + Confirmación Visual
│  - Dashboard    │  Monitoreo en Tiempo Real
└────────┬────────┘
         │ AWS IoT Core (HTTPS/MQTT)
         ↓
┌─────────────────┐
│  Cloud Layer    │  AWS
│  - IoT Core     │  Recepción de alertas
│  - Lambda       │  Procesamiento
│  - DynamoDB     │  Almacenamiento
│  - SNS/Telegram │  Notificaciones
└─────────────────┘
```

**Importante:**
- El sistema **funciona completamente sin AWS** (modo isla)
- AWS solo recibe **alertas confirmadas**, no todas las métricas
- El **dashboard debe estar en Fog** para ver todas las métricas en tiempo real

---

## ✅ Requisitos Previos

### Hardware
- **PC/Laptop** (Fog Node): 4GB RAM mínimo, conexión WiFi
- **Teléfono Android** (Cámara): Con Termux instalado
- **Arduino MKR WiFi 1010** (Opcional): Para sensores reales

### Software

#### En la PC (Fog Node):
```bash
# Python 3.8+
python3 --version

# Git
git --version

# Sistema operativo: Ubuntu/Debian (recomendado), macOS, o Windows WSL2
```

#### Cuenta AWS (Opcional):
- Credenciales IAM con permisos: IoT, Lambda, DynamoDB, SNS, S3
- Terraform instalado (si quieres desplegar con IaC)

---

## 🚀 Instalación Paso a Paso

### 1️⃣ Clonar el Repositorio

```bash
# Clonar proyecto
git clone <URL_DEL_REPOSITORIO> -b Jhon
cd Cloud-Fire-Detector

# Verificar rama
git branch
# Debe mostrar: * Jhon
```

---

### 2️⃣ Crear Entorno Virtual Python

```bash
# Crear entorno virtual en la raíz del proyecto
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Verificar activación (debe aparecer (.venv) en el prompt)
```

---

### 3️⃣ Instalar Dependencias Python

```bash
# Instalar dependencias del Fog Node
cd fog
pip install -r requirements.txt

# Instalar dependencias de los sensores Edge
cd ../edge
pip install -r requirements.txt

# Volver a la raíz
cd ..
```

**Dependencias principales:**
- `paho-mqtt`: Cliente MQTT
- `boto3`: SDK de AWS (solo si usas cloud)
- `requests`: Para comunicación HTTP con cámara
- `flask`: Para dashboard web (opcional)

---

### 4️⃣ Instalar y Configurar Mosquitto MQTT Broker

```bash
cd fog

# Instalar Mosquitto
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

# Ejecutar script de configuración automática
chmod +x setup_mosquitto.sh
sudo ./setup_mosquitto.sh
```

**El script configurará:**
- Broker escuchando en puerto `1883`
- Acceso desde red local (`0.0.0.0`)
- Logs en `/var/log/mosquitto/mosquitto.log`

**Verificar instalación:**
```bash
# Ver estado del servicio
sudo systemctl status mosquitto

# Debe mostrar: Active: active (running)
```

**Obtener IP de tu Fog Node:**
```bash
hostname -I | awk '{print $1}'
# Ejemplo de salida: 192.168.0.42
```

**⚠️ IMPORTANTE:** Anota esta IP, la necesitarás en el siguiente paso.

---

## ⚙️ Configuración del Sistema

### 5️⃣ Configurar Fog Processor

Edita el archivo `fog/fog_processor.py`:

```bash
nano fog/fog_processor.py
```

**Actualizar estas variables:**

```python
# Línea ~14: Broker MQTT Local
LOCAL_MQTT_BROKER = "localhost"  # Dejar como localhost

# Línea ~49-57: Mapa de Sensores → Cámaras
SENSOR_CAMERA_MAP = {
    "sensor-zona1": "192.168.0.XX",  # ⬅️ IP del teléfono con Termux
    "sensor-zona2": "192.168.0.XX",
    "sensor-virtual-1": "192.168.0.XX",
    "sensor-virtual-2": "192.168.0.XX",
    "sensor-virtual-3": "192.168.0.XX",
    "sensor-virtual-4": "192.168.0.XX",
    "sensor-virtual-5": "192.168.0.XX",
}

# Línea ~64: Conexión AWS (solo si tienes AWS configurado)
AWS_IOT_ENABLED = False  # ⬅️ Cambiar a True si usas AWS
```

**Guardar:** `Ctrl+O`, Enter, `Ctrl+X`

---

### 6️⃣ Configurar Sensores Virtuales

Edita el archivo `edge/sensores_virtuales.py`:

```bash
nano edge/sensores_virtuales.py
```

**Actualizar línea ~30:**
```python
MQTT_BROKER = "192.168.0.42"  # ⬅️ IP de tu Fog Node
```

**Guardar y cerrar.**

---

### 7️⃣ Configurar Cámara en Teléfono (OPCIONAL)

Si tienes un teléfono Android con Termux:

**En el teléfono:**
```bash
# Instalar Termux desde F-Droid (no Google Play)
# Abrir Termux y ejecutar:

pkg update
pkg install python termux-api
pip install flask pillow requests paho-mqtt

# Obtener IP del teléfono
ifconfig | grep "inet " | grep -v 127.0.0.1
# Ejemplo: 192.168.0.41

# Transferir el archivo termux_camera_server_simple.py al teléfono
# (puedes usar Termux:API o copiar manualmente)

# Ejecutar servidor de cámara
python termux_camera_server_simple.py
```

**⚠️ Importante:** 
- El teléfono debe estar en la **misma red WiFi** que el Fog Node
- Dar permisos de cámara a Termux en Android (Ajustes → Apps → Termux → Permisos)

**Actualizar IP en `fog_processor.py`** con la IP del teléfono (paso 5).

---

## 🏃 Ejecución del Sistema

### Iniciar Componentes (3 Terminales)

#### 🌫️ Terminal 1: Fog Processor

```bash
cd fog
source ../.venv/bin/activate
./start_fog.sh
```

**Salida esperada:**
```
======================================================================
🌫️  FOG PROCESSOR - Fire Detection System
======================================================================
✅ Conectado al broker MQTT local
📡 Suscrito a: industria/+/sensor/#
✅ Fog Processor en ejecución
   Esperando datos de sensores...
```

---

#### 📱 Terminal 2: Sensores Virtuales

```bash
cd edge
source ../.venv/bin/activate
python3 sensores_virtuales.py
```

**Salida esperada:**
```
📡 Sensores Virtuales - Fire Detection System
   Conectado a broker: 192.168.0.42:1883

✅ [sensor-virtual-1] T:25.3°C L:300 H:65.2% → zona2
✅ [sensor-virtual-2] T:23.1°C L:450 H:58.7% → zona3
...
```

---

#### 📸 Terminal 3 (Opcional): Servidor de Cámara

**En el teléfono (Termux):**
```bash
python termux_camera_server_simple.py
```

**Salida esperada:**
```
📷 SERVIDOR DE CÁMARA SIMPLIFICADO
🌐 Servidor en puerto 5000
📁 Imágenes en: /data/data/.../fire_detection_images
```

---

### 🧪 Verificar Funcionamiento

#### Monitorear Mensajes MQTT (Terminal 4):
```bash
mosquitto_sub -h localhost -t "industria/#" -v
```

Deberías ver mensajes como:
```
industria/zona2/sensor/sensor-virtual-1 {"device_id":"sensor-virtual-1","temperatura":25.3,...}
industria/zona3/sensor/sensor-virtual-2 {"device_id":"sensor-virtual-2","temperatura":23.1,...}
```

---

#### Probar Detección de Incendio:

**Opción 1: Esperar detección automática** (sensores virtuales tienen 1% probabilidad)

**Opción 2: Forzar detección con MQTT:**
```bash
mosquitto_pub -h localhost -t "industria/zona1/sensor/test" \
  -m '{"device_id":"sensor-test","temperatura":85.0,"luz":950,"humedad":15.0,"timestamp":"2025-12-29T12:00:00"}'
```

**En Terminal 1 (Fog) deberías ver:**
```
🚨 ALERTA: Posible incendio detectado en zona1
📸 Solicitando confirmación visual a cámara: 192.168.0.41
🔥🔥🔥 INCENDIO CONFIRMADO en zona1 🔥🔥🔥
```

---

## 📊 Dashboard de Monitoreo

### Iniciar Dashboard Web

```bash
cd fog
source ../.venv/bin/activate
python3 dashboard_fog.py
```

**Acceder desde navegador:**
- Local: `http://localhost:8080`
- Desde otro dispositivo: `http://192.168.0.42:8080` (usar IP de tu Fog Node)

**Características del Dashboard:**
- ✅ Métricas en tiempo real de todos los sensores
- ✅ Historial de alertas
- ✅ Estado del sistema
- ✅ Visualización por zonas

---

## ☁️ Integración con AWS (OPCIONAL)

Si quieres conectar el sistema con AWS Cloud para almacenamiento y notificaciones Telegram:

### 1️⃣ Configurar Credenciales AWS

```bash
# Instalar AWS CLI
sudo apt install awscli  # Ubuntu/Debian

# Configurar credenciales
aws configure
# AWS Access Key ID: <TU_ACCESS_KEY>
# AWS Secret Access Key: <TU_SECRET_KEY>
# Default region name: us-east-1
# Default output format: json

# Verificar configuración
aws sts get-caller-identity
```

---

### 2️⃣ Actualizar Variables de Terraform

```bash
cd Cloud-Fire-Detector
nano variables.tf
```

**Actualizar estas variables:**
```hcl
variable "fog_mqtt_broker_ip" {
  default = "192.168.0.42"  # ⬅️ IP de tu Fog Node
}

variable "sensor_camera_map" {
  default = {
    "sensor-zona1"     = "192.168.0.41"  # ⬅️ IP de tu cámara
    "sensor-virtual-1" = "192.168.0.41"
    # ... resto de sensores
  }
}

variable "telegram_bot_token" {
  default = "8128198300:AAEWmUMh6EDgU_mqlA7_ML54rw035KG3OlU"  # ⬅️ Tu token
}

variable "telegram_chat_id" {
  default = "6435171742"  # ⬅️ Tu chat ID
}
```

---

### 3️⃣ Desplegar Infraestructura con Terraform

```bash
# Inicializar Terraform
terraform init

# Ver plan de recursos a crear
terraform plan

# Desplegar (⚠️ GENERA COSTOS EN AWS)
terraform apply
# Escribe: yes
```

**Recursos que se crearán:**
- AWS IoT Core (Thing + Certificados)
- Lambda Functions (fire_handler, telegram)
- DynamoDB (tabla fire-events)
- SNS Topic (alertas)
- S3 Buckets (imágenes, logs)
- CloudWatch Logs
- IAM Roles y Políticas

---

### 4️⃣ Extraer Certificados IoT

```bash
# Ejecutar script de extracción
./extract_certs.sh

# Los certificados se guardarán en: fog/certs/
# - certificate.pem.crt
# - private.pem.key
# - AmazonRootCA1.pem
```

---

### 5️⃣ Habilitar AWS en Fog Processor

```bash
nano fog/fog_processor.py
```

**Cambiar línea 64:**
```python
AWS_IOT_ENABLED = True  # ⬅️ Cambiar de False a True
```

**Instalar SDK de AWS IoT:**
```bash
pip install awsiotsdk
```

**Reiniciar Fog Processor:**
```bash
cd fog
./start_fog.sh
```

---

### 6️⃣ Verificar Integración Cloud

**Ver logs de Lambda en CloudWatch:**
```bash
aws logs tail /aws/lambda/fire-event-handler --follow
```

**Ver eventos en DynamoDB:**
```bash
aws dynamodb scan --table-name fire-events --max-items 10
```

**Verificar Telegram:**
Deberías recibir notificaciones en Telegram cuando se detecte un incendio.

---

## 🐛 Troubleshooting

### Mosquitto no inicia

**Error:** `Job for mosquitto.service failed`

**Solución:**
```bash
# Ver error específico
sudo journalctl -xeu mosquitto.service | tail -20

# Validar configuración
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -t

# Si hay errores de permisos:
sudo chown -R mosquitto:mosquitto /var/lib/mosquitto/
sudo chown -R mosquitto:mosquitto /var/log/mosquitto/
sudo systemctl restart mosquitto
```

---

### Fog Processor no recibe mensajes

**Problema:** No aparecen logs de sensores

**Solución:**
```bash
# 1. Verificar que Mosquitto está corriendo
sudo systemctl status mosquitto

# 2. Verificar que sensores están publicando
mosquitto_sub -h localhost -t "industria/#" -v

# 3. Verificar IP del broker en sensores_virtuales.py
grep MQTT_BROKER edge/sensores_virtuales.py

# 4. Verificar firewall (si aplica)
sudo ufw allow 1883/tcp
```

---

### Cámara no responde

**Problema:** `Timeout al contactar cámara`

**Solución:**
```bash
# 1. Verificar que el servidor está corriendo en el teléfono
# En Termux: ps aux | grep python

# 2. Verificar IP del teléfono
# En Termux: ifconfig | grep inet

# 3. Probar conexión desde PC
curl http://192.168.0.41:5000/status

# 4. Verificar que están en la misma red WiFi
# PC: hostname -I
# Teléfono: ifconfig

# 5. Actualizar IP en fog_processor.py si cambió
```

---

### Error de instalación de OpenCV en Termux

**Problema:** `Failed to build opencv-python`

**Solución:**
```bash
# Usar versión simplificada (sin OpenCV)
# El proyecto incluye termux_camera_server_simple.py
# que NO requiere OpenCV

# Instalar solo dependencias básicas:
pip install flask pillow requests paho-mqtt
```

---

### Lambda falla con error de Decimal

**Problema:** `TypeError: Float types are not supported`

**Solución:**
```bash
# Verificar que fire_handler.py tiene la función convert_floats()
grep -A 10 "def convert_floats" lambda/fire_handler.py

# Si no la tiene, actualizar con la versión del repositorio

# Recrear ZIP y actualizar Lambda:
cd lambda
zip fire_handler.zip fire_handler.py
aws lambda update-function-code \
  --function-name fire-event-handler \
  --zip-file fileb://fire_handler.zip
```

---

### AWS IoT Core no recibe mensajes

**Problema:** Fog publica pero IoT Core no muestra actividad

**Solución:**
```bash
# 1. Verificar que AWS_IOT_ENABLED = True en fog_processor.py
grep AWS_IOT_ENABLED fog/fog_processor.py

# 2. Verificar certificados en fog/certs/
ls -la fog/certs/

# 3. Probar conexión con AWS IoT
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# 4. Ver logs del Fog Processor
tail -f fog/fog_processor.log
```

---

## 📦 Estructura del Proyecto

```
Cloud-Fire-Detector/
├── edge/                          # Capa Edge (Sensores)
│   ├── sensores_virtuales.py     # Sensores simulados
│   ├── termux_camera_server_simple.py  # Servidor de cámara
│   └── requirements.txt
│
├── fog/                           # Capa Fog (Procesamiento Local)
│   ├── fog_processor.py          # Orquestador principal
│   ├── dashboard_fog.py          # Dashboard web
│   ├── setup_mosquitto.sh        # Instalador de broker MQTT
│   ├── start_fog.sh              # Script de inicio
│   ├── certs/                    # Certificados AWS IoT (si se usa)
│   └── requirements.txt
│
├── lambda/                        # Funciones Lambda (AWS)
│   ├── fire_handler.py           # Procesa eventos de incendio
│   ├── telegram.py               # Envía notificaciones
│   └── *.zip                     # Paquetes para deployment
│
├── *.tf                          # Archivos Terraform (IaC)
├── variables.tf                  # Variables de configuración
├── outputs.tf                    # Outputs después del deploy
└── README.md                     # Esta guía
```

---

## 🎓 Validación del Sistema

### Checklist de Funcionamiento

- [ ] Mosquitto MQTT corriendo (`sudo systemctl status mosquitto`)
- [ ] Fog Processor recibiendo datos de sensores
- [ ] Sensores virtuales publicando métricas cada 5 segundos
- [ ] Cámara respondiendo a solicitudes (si se configuró)
- [ ] Dashboard web accesible en puerto 8080
- [ ] Detección de incendio funciona (temperatura > 60°C o luz > 800)
- [ ] Alertas se envían a Telegram (si AWS está configurado)
- [ ] Eventos se guardan en DynamoDB (si AWS está configurado)

---

## 📞 Soporte

**Proyecto desarrollado por:**
- Universidad Nacional de San Agustín
- Arequipa, Perú

**Repositorio:** [URL del repositorio]  
**Rama:** Jhon

---

## 📄 Licencia

[Especificar licencia del proyecto]

---

## 🎉 ¡Sistema Listo!

Si llegaste hasta aquí, tu sistema debería estar funcionando completamente:

```
Edge (Sensores) ✅ → Fog (Procesamiento) ✅ → Cloud (AWS) ✅
```

Para detener todos los servicios:
```bash
# Ctrl+C en cada terminal
# O desde otra terminal:
pkill -f fog_processor
pkill -f sensores_virtuales
pkill -f dashboard_fog
```

**¡Éxito en tu demostración! 🔥**
