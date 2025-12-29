# 📸 Configuración del Servidor de Cámara en Termux

## 🚀 Instalación Rápida

### 1️⃣ Instalar dependencias
```bash
bash install_termux_requirements.sh
```

### 2️⃣ Configurar credenciales AWS
```bash
bash setup_aws_termux.sh
```

O manualmente exportar variables:
```bash
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3️⃣ Ejecutar servidor
```bash
python termux_camera_server_simple.py
```

---

## 📋 Verificación

### Probar captura de foto:
```bash
termux-camera-photo test.jpg
```

### Probar servidor:
```bash
curl http://localhost:5000/status
```

### Probar desde laptop (fog node):
```bash
curl http://IP_TERMUX:5000/status
```

---

## 🔥 Flujo Completo con S3

Cuando se detecta fuego:

1. **Sensor** → Datos críticos → **Fog Node**
2. **Fog Node** → Solicitud → **Cámara Termux**
3. **Cámara** → Captura foto → Analiza
4. **Cámara** → Sube a S3 (si hay fuego)
5. **Cámara** → Responde con `{fire_detected, confidence, s3_key, s3_url}`
6. **Fog Node** → Envía alerta a **AWS IoT** (con URL de imagen)
7. **Lambda** → Procesa → Guarda en **DynamoDB** → **Telegram**

---

## 🗂️ Estructura de S3

```
s3://fire-detection-images-577272335685/
  └── detections/
      └── zona1/
          └── sensor-zona1/
              ├── 20251229_120000.jpg
              ├── 20251229_120530.jpg
              └── ...
```

---

## 🔍 Logs del Servidor

```
📸 Solicitud de sensor-zona1 (zona: zona1)
📷 Foto capturada: /storage/emulated/0/fire_detection_images/capture_20251229_120000.jpg
🔍 Analizando con método simplificado...
🔥 FUEGO DETECTADO (confianza: 68.5%)
☁️ Subiendo imagen a S3: detections/zona1/sensor-zona1/20251229_120000.jpg
✅ Imagen subida a S3
```

---

## ⚙️ Configuración

| Variable | Valor |
|----------|-------|
| Puerto | 5000 |
| Bucket S3 | fire-detection-images-577272335685 |
| Región AWS | us-east-1 |
| Umbral Temperatura | > 60°C |
| Umbral Luz | > 800 |

---

## 🐛 Troubleshooting

### Error: "S3 client no disponible"
- Verifica que boto3 esté instalado: `pip list | grep boto3`
- Verifica credenciales: `cat ~/.aws/credentials`

### Error: "termux-camera-photo command not found"
- Instala Termux:API: `pkg install termux-api`
- Instala la app Termux:API desde F-Droid o Play Store

### Error: "Permission denied"
- Otorga permisos de cámara a Termux en configuración de Android

### Cámara no responde desde fog node
- Verifica que estén en la misma WiFi
- Verifica IP: `ip addr show wlan0`
- Prueba: `curl http://localhost:5000/test`
