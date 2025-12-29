# ✅ Configuración AWS IoT Completada

**Fecha**: 29 de diciembre de 2025  
**Usuario AWS**: jhon (Account: 577272335685)

---

## 🎯 Estado del Sistema

### ✅ Software Instalado

- **AWS CLI**: v2.32.24
- **Terraform**: v1.14.3
- **CMake**: v3.28.3
- **AWS IoT SDK**: v1.12.0
- **Python**: 3.12.3 con entorno virtual

### ✅ Infraestructura AWS Desplegada

| Recurso | Detalle |
|---------|---------|
| **IoT Core Thing** | fog-node-001 |
| **IoT Endpoint** | a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com |
| **Lambda Functions** | fire-event-handler, telegram-notifier |
| **DynamoDB Table** | fire-events |
| **SNS Topic** | fire-detection-alerts |
| **S3 Buckets** | fire-detection-images, terraform-state |
| **API Gateway** | https://tnzk1r6dpg.execute-api.us-east-1.amazonaws.com |

### ✅ Certificados IoT

Ubicación: `fog/certs/`

```
fog/certs/
├── certificate.pem.crt    (1.2 KB) - Certificado del dispositivo
├── private.pem.key        (1.7 KB) - Clave privada
└── AmazonRootCA1.pem      (1.2 KB) - Root CA de Amazon
```

### ✅ Configuración del Fog

Archivo: `fog/config/settings.py`

```python
AWS_IOT_ENABLED = True
AWS_IOT_ENDPOINT = "a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com"
AWS_IOT_CLIENT_ID = "fog-node-001"
AWS_CERT_PATH = "fog/certs/certificate.pem.crt"
AWS_PRIVATE_KEY_PATH = "fog/certs/private.pem.key"
AWS_ROOT_CA_PATH = "fog/certs/AmazonRootCA1.pem"
```

---

## 🚀 Flujo de Datos Completo

```
┌──────────────────────┐
│ Sensores Virtuales   │  Temperatura, Luz, Humedad
│ (edge/)              │  Cada 5 segundos
└──────────┬───────────┘
           │ MQTT: localhost:1883
           ↓
┌──────────────────────┐
│ Mosquitto Broker     │  Puerto 1883
└──────────┬───────────┘
           │ Topic: industria/+/sensor/#
           ↓
┌──────────────────────┐
│ Fog Processor        │  1. Analiza umbrales
│ (fog_processor.py)   │  2. Detecta incendios
│                      │  3. Confirma con cámara
└──────────┬───────────┘
           │ 🔥 Solo si INCENDIO CONFIRMADO
           ↓
┌──────────────────────┐
│ AWS IoT Core         │  Certificados TLS
│ (MQTT sobre TLS)     │  Topic: industria/zona1/alertas
└──────────┬───────────┘
           │ IoT Rule: fire_alert_processor
           ↓
┌──────────────────────┐
│ Lambda Function      │  fire-event-handler
│ (fire_handler.py)    │  Procesa alerta
└──────────┬───────────┘
           │
           ├─→ DynamoDB (fire-events) - Almacenamiento
           │
           └─→ SNS Topic (fire-detection-alerts)
                    │
                    └─→ Lambda (telegram-notifier)
                              │
                              └─→ 📱 Telegram
```

---

## 📋 Comandos Útiles

### Ejecutar el Sistema

```bash
# Opción 1: Automático (Recomendado)
./start_project.sh
# → Seleccionar opción 3

# Opción 2: Manual (2 terminales)
# Terminal 1:
source .venv/bin/activate
python3 edge/sensores_virtuales.py

# Terminal 2:
source .venv/bin/activate
python3 fog/fog_processor.py
```

### Monitoreo

```bash
# Ver mensajes MQTT locales
mosquitto_sub -h localhost -t '#' -v

# Ver logs de AWS IoT
aws iot-data get-thing-shadow --thing-name fog-node-001

# Ver eventos en DynamoDB
aws dynamodb scan --table-name fire-events --max-items 5

# Ver logs de Lambda
aws logs tail /aws/lambda/fire-event-handler --follow
```

### Terraform

```bash
# Ver outputs
terraform output

# Ver certificado IoT
terraform output -raw iot_certificate_pem

# Destruir infraestructura (¡cuidado!)
terraform destroy
```

---

## 🔍 Verificación del Sistema

### Test 1: Conexión AWS IoT

El fog processor debería mostrar:
```
☁️  Conectado a AWS IoT Core
```

### Test 2: Detección de Incendio

Cuando un sensor envíe valores críticos:
```
🚨 Riesgo de incendio en zona zona2
   🌡️ 85.0°C 🔥
   💡 950 🔥
🔥 INCENDIO CONFIRMADO en zona2
☁️  Alerta enviada a AWS IoT Core
```

### Test 3: Verificar en AWS

```bash
# Ver última entrada en DynamoDB
aws dynamodb scan --table-name fire-events \
  --max-items 1 \
  --scan-index-forward false
```

---

## ⚠️ Troubleshooting

### Error: "Could not connect to AWS IoT"

```bash
# Verificar certificados
ls -lh fog/certs/

# Verificar endpoint
cat fog/config/settings.py | grep AWS_IOT_ENDPOINT

# Probar conexión con mosquitto_pub
mosquitto_pub --cafile fog/certs/AmazonRootCA1.pem \
  --cert fog/certs/certificate.pem.crt \
  --key fog/certs/private.pem.key \
  -h a7a75jxclqem3-ats.iot.us-east-1.amazonaws.com \
  -p 8883 -t test/topic -m "test"
```

### Error: "AWS IoT SDK not found"

```bash
source .venv/bin/activate
pip install awsiotsdk==1.12.0
```

### Error al compilar awscrt

```bash
# Instalar dependencias
sudo apt install -y cmake build-essential libssl-dev
```

---

## 📊 Costos Estimados AWS

**Uso mensual estimado** (modo desarrollo):

| Servicio | Uso | Costo/mes |
|----------|-----|-----------|
| IoT Core | ~10,000 mensajes | $0.80 |
| Lambda | ~1,000 invocaciones | $0.00 (Free Tier) |
| DynamoDB | On-Demand, <1GB | $0.25 |
| SNS | ~100 notificaciones | $0.00 (Free Tier) |
| S3 | <5GB | $0.12 |
| **Total** | | **~$1.17/mes** |

> 💡 **Nota**: Free Tier de AWS cubre gran parte del uso durante el primer año.

---

## 🔐 Seguridad

### Permisos IAM Configurados

- Lambda tiene acceso a: DynamoDB, SNS, CloudWatch Logs
- IoT Policy permite: Publicar y suscribirse a topics específicos
- Certificados IoT: Autenticación mutual TLS (mTLS)

### Recomendaciones

1. ✅ Rotar certificados cada 90 días
2. ✅ Usar IAM roles específicos (no credenciales de root)
3. ✅ Habilitar CloudTrail para auditoría
4. ✅ Configurar alertas de costos en AWS Budgets

---

## 📞 Soporte

- **Documentación AWS IoT**: https://docs.aws.amazon.com/iot/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/

---

**Sistema configurado por**: GitHub Copilot  
**Proyecto**: Cloud Fire Detector - UNSA Arequipa, Perú

---

✅ **Todo listo para producción local con respaldo en la nube**
