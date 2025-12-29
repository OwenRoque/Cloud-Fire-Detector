# 🚀 Guía Rápida - Levantar el Proyecto

> **Cloud Fire Detector** - Sistema de detección de incendios Edge-Fog-Cloud  
> Universidad Nacional de San Agustín - Arequipa, Perú

---

## 📋 Resumen

Este proyecto tiene 3 componentes principales que se ejecutan en orden:

1. **Mosquitto (MQTT Broker)** - Debe estar encendido
2. **Sensores Virtuales** (`edge/sensores_virtuales.py`) - Generan datos simulados
3. **Fog Processor** (`fog/fog_processor.py`) - Procesa datos y se conecta a AWS IoT

---

## ✅ Pre-requisitos

- **Sistema Operativo**: Linux (Ubuntu/Debian recomendado)
- **Python**: 3.8 o superior
- **Conexión a Internet**: Para instalar dependencias (solo primera vez)

---

## 🚀 Instalación (Primera vez)

### Paso 1: Instalar Dependencias del Sistema

```bash
# Dar permisos de ejecución
chmod +x setup_system.sh setup_python.sh start_project.sh

# Instalar Mosquitto MQTT Broker (requiere sudo)
sudo ./setup_system.sh
```

**Esto instalará:**
- Mosquitto MQTT Broker
- Configurará el puerto 1883
- Habilitará el servicio automático

---

### Paso 2: Configurar Python y Dependencias

```bash
# Crear entorno virtual e instalar dependencias
./setup_python.sh
```

**Esto hará:**
- Crear entorno virtual en `.venv/`
- Instalar dependencias del Fog Layer
- Instalar dependencias del Edge Layer
- Verificar certificados AWS IoT (si existen)

---

## 🎯 Ejecución del Proyecto

### Opción A: Script Automático (Recomendado)

```bash
./start_project.sh
```

**Menú interactivo con opciones:**
1. Iniciar solo Sensores Virtuales
2. Iniciar solo Fog Processor
3. **Iniciar ambos (recomendado)** - Abre 2 terminales automáticamente
4. Verificar estado del sistema
5. Salir

---

### Opción B: Manual (2 Terminales)

#### Terminal 1: Sensores Virtuales

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar sensores
python3 edge/sensores_virtuales.py
```

**Salida esperada:**
```
📡 Iniciando sensores virtuales...
✅ Conectado al broker MQTT
📤 [sensor-virtual-1] Enviando datos...
📤 [sensor-virtual-2] Enviando datos...
...
```

#### Terminal 2: Fog Processor (esperar 5-10 segundos después de iniciar sensores)

```bash
# Activar entorno virtual
source .venv/bin/activate

# IMPORTANTE: Ejecutar desde la raíz del proyecto
# (donde está terraform.tfstate, si existe)
python3 fog/fog_processor.py
```

**Salida esperada:**
```
🌫️  FOG PROCESSOR - Fire Detection System
======================================================================
✅ Conectado al broker MQTT local
📡 Suscrito a industria/+/sensor/#
📥 Datos recibidos de sensor-virtual-1 (zona zona2)
   🌡️ 25.3°C ✅
   💡 350 ✅
   💧 55% ✅
```

---

## 🔍 Verificar que Todo Funciona

### 1. Verificar Mosquitto

```bash
# Ver estado del servicio
sudo systemctl status mosquitto

# Debería mostrar: Active: active (running)
```

### 2. Monitorear Mensajes MQTT (Terminal 3 - Opcional)

```bash
# Ver todos los mensajes en tiempo real
mosquitto_sub -h localhost -t '#' -v
```

**Deberías ver:**
```
industria/zona2/sensor/sensor-virtual-1 {"device_id":"sensor-virtual-1",...}
industria/zona3/sensor/sensor-virtual-2 {"device_id":"sensor-virtual-2",...}
...
```

### 3. Verificar Estado Completo del Sistema

```bash
./start_project.sh
# Seleccionar opción 4
```

---

## 🌐 Conexión con AWS IoT

### ¿Tienes Terraform State?

Si ya desplegaste la infraestructura con Terraform y tienes certificados:

1. **Verificar certificados:**
   ```bash
   ls -la fog/certs/
   # Deberías ver:
   # - certificate.pem.crt
   # - private.pem.key
   # - AmazonRootCA1.pem
   ```

2. **AWS IoT se habilitará automáticamente** cuando ejecutes el Fog Processor

### ¿NO tienes Terraform State?

El sistema funcionará en **Modo Local (Modo Isla)**:
- ✅ Sensores envían datos al Fog
- ✅ Fog procesa y detecta incendios
- ✅ Confirmación visual funciona (si tienes cámara)
- ❌ NO se envía a AWS IoT Cloud
- ❌ NO hay notificaciones a Telegram

Para habilitar AWS IoT:
```bash
# 1. Configurar credenciales AWS
aws configure

# 2. Desplegar infraestructura
terraform init
terraform apply

# 3. Los certificados se crearán automáticamente
# 4. Re-ejecutar setup_python.sh para instalar AWS IoT SDK
./setup_python.sh
```

---

## 🛠️ Comandos Útiles

### Mosquitto

```bash
# Iniciar servicio
sudo systemctl start mosquitto

# Detener servicio
sudo systemctl stop mosquitto

# Reiniciar servicio
sudo systemctl restart mosquitto

# Ver logs
sudo journalctl -u mosquitto -f
```

### Entorno Virtual Python

```bash
# Activar (siempre desde la raíz del proyecto)
source .venv/bin/activate

# Desactivar
deactivate

# Ver paquetes instalados
pip list
```

### Proyecto

```bash
# Detener componentes
# Presionar Ctrl+C en cada terminal

# Ver configuración del Fog
cat fog/config/settings.py

# Ver mapeo de cámaras
cat fog/fog_config.json
```

---

## 🐛 Troubleshooting

### Error: "Mosquitto no está corriendo"

```bash
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

### Error: "Entorno virtual no encontrado"

```bash
./setup_python.sh
```

### Error: "ModuleNotFoundError: No module named 'paho'"

```bash
# Verificar que el entorno virtual esté activado
source .venv/bin/activate

# Reinstalar dependencias
cd fog && pip install -r requirements.txt
cd ../edge && pip install -r requirements.txt
```

### Fog Processor no recibe mensajes

1. **Verificar que Mosquitto esté corriendo:**
   ```bash
   sudo systemctl status mosquitto
   ```

2. **Verificar que los sensores estén enviando datos:**
   ```bash
   mosquitto_sub -h localhost -t '#' -v
   ```

3. **Verificar configuración MQTT:**
   - Archivo: `fog/config/settings.py`
   - Verificar: `LOCAL_MQTT_BROKER = "localhost"`

### AWS IoT no conecta

1. **Verificar certificados:**
   ```bash
   ls -la fog/certs/
   ```

2. **Verificar configuración:**
   ```bash
   cat fog/config/settings.py | grep AWS_IOT
   ```

3. **Verificar endpoint:**
   ```bash
   terraform output iot_endpoint
   ```

---

## 📊 Flujo de Datos

```
┌──────────────────┐
│ Sensores         │  Cada 5 segundos
│ Virtuales        │  Temperatura, Luz, Humedad
│ (Python)         │
└────────┬─────────┘
         │ MQTT: industria/zona#/sensor/#
         ↓
┌──────────────────┐
│ Mosquitto        │  Puerto 1883
│ (MQTT Broker)    │  localhost
└────────┬─────────┘
         │ Suscripción: industria/+/sensor/#
         ↓
┌──────────────────┐
│ Fog Processor    │  1. Recibe datos
│ (Python)         │  2. Analiza umbrales
│                  │  3. Si crítico → Pide foto
│                  │  4. Si fuego → AWS IoT
└────────┬─────────┘
         │ HTTPS/MQTT (si AWS habilitado)
         ↓
┌──────────────────┐
│ AWS IoT Core     │  → Lambda → DynamoDB
│                  │  → SNS → Telegram
└──────────────────┘
```

---

## 📝 Notas Importantes

1. **Siempre ejecutar desde la raíz del proyecto** donde está `terraform.tfstate` (si existe)

2. **Orden de inicio:**
   - 1️⃣ Mosquitto (debe estar corriendo)
   - 2️⃣ Sensores Virtuales
   - 3️⃣ Fog Processor (después de 5-10 segundos)

3. **Modo Local vs Cloud:**
   - **Sin certificados AWS**: Funciona localmente, no envía a cloud
   - **Con certificados AWS**: Envía alertas confirmadas a AWS IoT

4. **Para detener:**
   - `Ctrl+C` en cada terminal
   - El sistema se detendrá limpiamente

---

## 📞 Contacto

Universidad Nacional de San Agustín - Arequipa, Perú  
Proyecto: Cloud Fire Detector  
Arquitectura: Edge-Fog-Cloud

---

## ✅ Checklist de Primera Ejecución

- [ ] Ejecutar `sudo ./setup_system.sh`
- [ ] Verificar Mosquitto: `sudo systemctl status mosquitto`
- [ ] Ejecutar `./setup_python.sh`
- [ ] Verificar entorno virtual: `source .venv/bin/activate`
- [ ] Ejecutar `./start_project.sh` y elegir opción 3
- [ ] Verificar que sensores envían datos
- [ ] Verificar que fog processor recibe datos
- [ ] (Opcional) Configurar cámara en `fog/fog_config.json`
- [ ] (Opcional) Desplegar AWS con `terraform apply`

¡Listo! 🔥
