# 🔥 Flujo de Imágenes - Fire Detection System

## 📋 Arquitectura Actualizada

```
┌─────────────┐
│   Arduino   │ Sensor físico con MKR WiFi 1010
│   MKR 1010  │ Detecta: Temperatura, Luz, Humedad
└──────┬──────┘
       │ MQTT (industria/zona1/sensor/arduino)
       ▼
┌─────────────────────────────────────────────────────────┐
│              FOG NODE (Laptop Ubuntu)                   │
│                                                         │
│  1. Recibe datos del sensor                            │
│  2. Analiza umbrales (temp>60°C o luz>800)             │
│  3. Si detecta anomalía → Solicita cámara              │
│     ┌────────────────────────────────────┐             │
│     │ POST http://CAMARA_IP:5000/capturar│             │
│     │ {"sensor_id": "...", "zona": "..."} │             │
│     └────────────────────────────────────┘             │
│                                                         │
│  4. Recibe respuesta:                                  │
│     {                                                   │
│       "fire_detected": true,                           │
│       "confidence": 0.85,                              │
│       "image_data": "base64_encoded_image"  ◄─────┐   │
│     }                                               │   │
│                                                     │   │
│  5. Si fire_detected = true:                       │   │
│     ├─ Sube imagen a S3 ───────────────────────┐   │   │
│     │                                           │   │   │
│     └─ Publica alerta en AWS IoT Core          │   │   │
│        {                                        │   │   │
│          "fuego_detectado": true,              │   │   │
│          "image_s3_key": "detections/...",     │   │   │
│          "image_url": "https://s3..."          │   │   │
│        }                                        │   │   │
└─────────────────────────────────────────────────┼───┼───┘
                                                  │   │
                        ┌─────────────────────────┘   │
                        ▼                             │
              ┌──────────────────┐                    │
              │   AWS S3 Bucket  │                    │
              │ fire-detection-  │                    │
              │ images-5772...   │                    │
              │                  │                    │
              │ /detections/     │                    │
              │   /zona1/        │                    │
              │     /sensor-1/   │                    │
              │       /*.jpg     │                    │
              └──────────────────┘                    │
                        │                             │
                        ▼                             │
              ┌──────────────────┐                    │
              │   AWS IoT Core   │                    │
              └────────┬─────────┘                    │
                       │                              │
                       ▼                              │
              ┌──────────────────┐                    │
              │  Lambda Function │                    │
              └────────┬─────────┘                    │
                       │                              │
              ┌────────┴─────────┐                    │
              ▼                  ▼                    │
      ┌──────────────┐   ┌──────────────┐            │
      │  DynamoDB    │   │   Telegram   │            │
      │  (Historial) │   │ (Notificación)│            │
      └──────────────┘   └──────────────┘            │
                                                      │
┌─────────────────────────────────────────────────────┘
│         CÁMARA (Termux Android)                    
│                                                     
│  1. Recibe POST /capturar                          
│  2. Ejecuta: termux-camera-photo                   
│  3. Analiza imagen (simulado o con IA)             
│  4. Si detecta fuego:                              
│     ├─ Codifica imagen en base64                   
│     └─ Retorna JSON con image_data                 
│                                                     
│  ⚠️ NO SUBE A S3 DIRECTAMENTE                      
│     (Fog Node maneja S3)                           
└─────────────────────────────────────────────────────┘
```

## 🔄 Ventajas del Nuevo Flujo

### ✅ Cámara Simplificada
- **Sin configurar AWS en Termux**
- Solo necesita: Flask + requests
- No requiere credenciales AWS
- Menor consumo de datos móviles

### ✅ Fog Node Centralizado
- **Control total del storage**
- Todas las credenciales AWS en un solo lugar
- Puede guardar copias locales antes de subir
- Mejor gestión de errores de red

### ✅ Eficiencia de Red
- Imagen se transmite una sola vez (Cámara → Fog)
- Base64 sobre HTTP (comprimido con gzip)
- Fog Node puede comprimir antes de subir a S3

## 📝 Formato de Datos

### Cámara → Fog Node
```json
{
  "fire_detected": true,
  "confidence": 0.85,
  "timestamp": "2025-12-29T12:00:00",
  "sensor_id": "sensor-zona1",
  "zona": "zona1",
  "image_data": "/9j/4AAQSkZJRgABAQEAYABgAAD...",  # Base64
  "image_format": "jpeg",
  "method": "simple"
}
```

### Fog Node → AWS IoT
```json
{
  "device_id": "sensor-zona1",
  "zona": "zona1",
  "ubicacion": "Planta Industrial - zona1",
  "fuego_detectado": true,
  "confidence": 0.85,
  "temperatura": 65.2,
  "luz": 1200,
  "humedad": 28.5,
  "timestamp": "2025-12-29T12:00:00Z",
  "image_s3_key": "detections/zona1/sensor-zona1/20251229_120000.jpg",
  "image_url": "https://fire-detection-images-577272335685.s3.us-east-1.amazonaws.com/detections/..."
}
```

## 🚀 Ejecución

### En Laptop (Fog Node)
```bash
cd ~/Cloud-Fire-Detector
source .venv/bin/activate

# Ya tiene boto3 instalado
python3 fog/fog_processor.py
```

### En Termux (Cámara)
```bash
# Solo necesita Flask (sin boto3)
pip install flask requests

python termux_camera_server_simple.py
```

## 📦 Estructura S3

```
fire-detection-images-577272335685/
└── detections/
    ├── zona1/
    │   └── sensor-zona1/
    │       ├── 20251229_120000.jpg
    │       ├── 20251229_120530.jpg
    │       └── 20251229_121005.jpg
    ├── zona2/
    │   └── sensor-zona2/
    │       └── ...
    └── zona3/
        └── sensor-virtual-2/
            └── ...
```

## 🔐 Permisos IAM Requeridos

El usuario IAM (jhon) necesita:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:PutObjectAcl"
  ],
  "Resource": "arn:aws:s3:::fire-detection-images-577272335685/detections/*"
}
```

## 📊 Tamaño Estimado

- Imagen JPEG: ~200-500 KB
- Base64 overhead: +33%
- JSON total: ~300-700 KB por alerta

## ⚡ Optimizaciones Futuras

1. **Compresión de imagen** antes de codificar base64
2. **WebP format** (menor tamaño que JPEG)
3. **Streaming** en lugar de base64 (multipart/form-data)
4. **Thumbnail** en la respuesta + imagen completa async
