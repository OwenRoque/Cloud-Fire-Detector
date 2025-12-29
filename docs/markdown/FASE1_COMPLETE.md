# Fase 1: Infraestructura Cloud (COMPLETADA ✅)

## Resumen de Cambios

### Archivos Modificados
- ✅ `iot.tf` - IoT Core Thing, Policy, Certificate, IoT Rule
- ✅ `greengrass_v2.tf` - IAM Roles, Thing Group, S3 Artifacts
- ✅ `variables.tf` - Mapa de proximidad sensor-cámara
- ✅ `outputs.tf` - Certificados y endpoints
- ✅ `lambda-telegram.tf` - Variables para tokens
- ✅ `versions.tf` - Provider AWS 5.30+

### Nuevos Recursos Creados
1. **IoT Core:**
   - Thing: `fog-node-001`
   - Policy con permisos Publish/Subscribe/Receive
   - Certificado X.509 para mTLS
   - IoT Rule para procesar alertas → Lambda

2. **Greengrass v2:**
   - IAM Role: `GreengrassCoreTokenExchangeRole`
   - Role Alias para credenciales temporales
   - Thing Group: `fog-computing-nodes`
   - S3 Bucket para artefactos
   - Configuración JSON en S3

3. **Variables configurables:**
   - `sensor_camera_map` - Mapeo sensor ID → IP cámara
   - `fog_mqtt_broker_ip` - IP del bróker MQTT local
   - `telegram_bot_token` / `telegram_chat_id`

## Deployment

### 1. Configurar variables sensibles

Crea un archivo `terraform.tfvars` (NO commitear a Git):

```hcl
telegram_bot_token = "1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
telegram_chat_id   = "987654321"
fog_mqtt_broker_ip = "192.168.1.100"  # IP de tu Laptop B

sensor_camera_map = {
  "sensor-zona1"     = "192.168.1.105"  # IP del celular con Termux
  "sensor-virtual-1" = "192.168.1.105"
  "sensor-virtual-2" = "192.168.1.105"
  "sensor-virtual-3" = "192.168.1.105"
  "sensor-virtual-4" = "192.168.1.105"
  "sensor-virtual-5" = "192.168.1.105"
}
```

Añade a `.gitignore`:
```
terraform.tfvars
*.tfstate
*.tfstate.backup
fog/certs/
```

### 2. Validar y planificar

```bash
terraform fmt
terraform validate
terraform plan -out=tfplan
```

### 3. Aplicar infraestructura

```bash
terraform apply tfplan
```

### 4. Extraer certificados

```bash
./extract_certs.sh
```

Esto creará el directorio `./fog/certs/` con:
- `certificate.pem.crt`
- `private.pem.key`
- `public.pem.key`
- `AmazonRootCA1.pem`

### 5. Verificar outputs

```bash
terraform output
```

Outputs importantes:
- `iot_endpoint` - Endpoint MQTT de AWS IoT Core
- `greengrass_role_alias` - Alias del Role para Greengrass
- `greengrass_config_s3_uri` - Configuración del Fog en S3

## Próximos Pasos (Fase 2)

1. **Fog Node (Laptop B):**
   - Instalar Mosquitto MQTT Broker
   - Crear `fog_processor.py`
   - Instalar AWS IoT Greengrass v2 Core Device

2. **Edge Devices:**
   - Modificar Arduino `.ino` para apuntar a IP local
   - Crear sensores virtuales en Python

3. **Visión Artificial:**
   - Script Termux para captura de cámara

## Arquitectura Actual

```
┌─────────────────────────────────────────────────────────┐
│                      AWS CLOUD                          │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐  │
│  │  IoT Core    │──▶│   Lambda     │──▶│  Telegram  │  │
│  │ fog-node-001 │   │fire_handler  │   │    Bot     │  │
│  └──────┬───────┘   └──────────────┘   └────────────┘  │
│         │                   │                           │
│         │           ┌───────▼────────┐                  │
│         │           │   DynamoDB     │                  │
│         │           │  fire-events   │                  │
│         │           └────────────────┘                  │
└─────────┼───────────────────────────────────────────────┘
          │ mTLS (X.509)
          │
┌─────────▼────────────────────────────────────────────┐
│              LAPTOP B - FOG NODE                     │
│  ┌─────────────────────────────────────────────────┐ │
│  │     AWS IoT Greengrass v2 Core Device           │ │
│  │  ┌───────────────────────────────────────────┐  │ │
│  │  │       fog_processor.py (Pendiente)        │  │ │
│  │  │  - Escucha sensores MQTT locales          │  │ │
│  │  │  - Lógica de umbrales críticos            │  │ │
│  │  │  - Solicita confirmación visual (cámara)  │  │ │
│  │  │  - Publica alertas a AWS IoT Core         │  │ │
│  │  └───────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │      Mosquitto MQTT Broker (1883)               │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
          │ MQTT local
          │
┌─────────▼────────────────────────────────────────────┐
│                    EDGE DEVICES                      │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ Arduino MKR    │  │  Sensores Virtuales (5x) │   │
│  │ WiFi 1010      │  │  (Laptop A - Python)     │   │
│  └────────────────┘  └──────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │    Celular con Termux (Cámara + OpenCV)     │   │
│  │    - Flask server en puerto 5000             │   │
│  │    - Endpoint /capturar                      │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Comandos Útiles

### Ver logs de IoT Rule
```bash
aws logs tail /aws/iot/rules/fire_alert_processor --follow --region us-east-1
```

### Probar publicación MQTT (desde Laptop B)
```bash
aws iot-data publish \
  --topic "industria/zona1/alertas" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"device_id":"test","fuego_detectado":true,"confidence":0.95,"temperatura":65}'
```

### Listar Things
```bash
aws iot list-things
```

### Verificar certificado
```bash
openssl x509 -in fog/certs/certificate.pem.crt -text -noout
```
