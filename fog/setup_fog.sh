#!/bin/bash
# ============================================================================
# Setup Fog Processor - Configuración Local
# ============================================================================
# Ejecutar DESPUÉS de terraform apply
# Descarga configuración desde S3 y prepara el entorno
# ============================================================================

set -e

echo "🌫️  Configurando Fog Processor..."
echo ""

# Directorio base
FOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${FOG_DIR}/certs"
CONFIG_FILE="${FOG_DIR}/fog_config.json"

# ============================================================================
# 1. Verificar Python y virtualenv
# ============================================================================
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION detectado"
echo ""

# Crear virtualenv si no existe
if [[ ! -d "${FOG_DIR}/.venv" ]]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv "${FOG_DIR}/.venv"
    echo "✅ Virtualenv creado en ${FOG_DIR}/.venv"
fi

# Activar virtualenv
source "${FOG_DIR}/.venv/bin/activate"

# Instalar dependencias
echo ""
echo "📥 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r "${FOG_DIR}/requirements.txt"
echo "✅ Dependencias instaladas"
echo ""

# ============================================================================
# 2. Descargar configuración desde S3 (si existe)
# ============================================================================
echo "☁️  Descargando configuración desde S3..."

# Obtener URI de S3 desde Terraform
if command -v terraform &> /dev/null && [[ -f "../terraform.tfstate" ]]; then
    S3_CONFIG_URI=$(cd .. && terraform output -raw greengrass_config_s3_uri 2>/dev/null || echo "")
    
    if [[ -n "$S3_CONFIG_URI" ]]; then
        echo "   URI: ${S3_CONFIG_URI}"
        
        # Descargar con AWS CLI
        if aws s3 cp "$S3_CONFIG_URI" "$CONFIG_FILE" 2>/dev/null; then
            echo "✅ Configuración descargada: ${CONFIG_FILE}"
        else
            echo "⚠️  No se pudo descargar (AWS CLI no configurado o sin permisos)"
            echo "   Usando configuración por defecto"
        fi
    else
        echo "⚠️  Terraform no aplicado todavía"
        echo "   Usando configuración por defecto"
    fi
else
    echo "⚠️  Terraform no disponible"
    echo "   Usando configuración por defecto"
fi

# Crear configuración por defecto si no existe
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo ""
    echo "📝 Creando configuración por defecto..."
    
    cat > "$CONFIG_FILE" <<'EOF'
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
EOF
    echo "✅ Configuración por defecto creada"
fi

echo ""

# ============================================================================
# 3. Verificar certificados IoT (si existen)
# ============================================================================
echo "🔐 Verificando certificados..."

if [[ -d "$CERT_DIR" ]] && [[ -f "${CERT_DIR}/certificate.pem.crt" ]]; then
    echo "✅ Certificados encontrados:"
    ls -lh "$CERT_DIR"
    
    # Verificar permisos
    if [[ -r "${CERT_DIR}/private.pem.key" ]]; then
        echo "✅ Permisos de certificados OK"
    else
        echo "⚠️  Ajustando permisos..."
        chmod 600 "${CERT_DIR}"/*.key 2>/dev/null || true
    fi
else
    echo "⚠️  Certificados no encontrados"
    echo "   Ejecuta ../extract_certs.sh después de terraform apply"
fi

echo ""

# ============================================================================
# 4. Verificar Mosquitto
# ============================================================================
echo "🦟 Verificando Mosquitto..."

if systemctl is-active --quiet mosquitto 2>/dev/null; then
    echo "✅ Mosquitto está corriendo"
    BROKER_IP=$(hostname -I | awk '{print $1}')
    echo "   Broker: mqtt://${BROKER_IP}:1883"
elif command -v mosquitto &> /dev/null; then
    echo "⚠️  Mosquitto instalado pero no está corriendo"
    echo "   Ejecuta: sudo systemctl start mosquitto"
else
    echo "❌ Mosquitto no está instalado"
    echo "   Ejecuta: ./setup_mosquitto.sh"
fi

echo ""

# ============================================================================
# 5. Crear script de inicio rápido
# ============================================================================
echo "📝 Creando script de inicio..."

cat > "${FOG_DIR}/start_fog.sh" <<'EOF'
#!/bin/bash
# Script de inicio rápido para Fog Processor
cd "$(dirname "$0")"
source .venv/bin/activate
python3 fog_processor.py
EOF

chmod +x "${FOG_DIR}/start_fog.sh"
echo "✅ Script creado: ${FOG_DIR}/start_fog.sh"

echo ""
echo "=" * 70
echo "✅ Fog Processor configurado correctamente"
echo "=" * 70
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Verificar/editar configuración:"
echo "   nano fog_config.json"
echo ""
echo "2. Iniciar Fog Processor:"
echo "   ./start_fog.sh"
echo ""
echo "   O manualmente:"
echo "   source .venv/bin/activate"
echo "   python3 fog_processor.py"
echo ""
echo "3. En otra terminal, probar con sensor virtual:"
echo "   mosquitto_pub -h localhost -t 'industria/zona1/sensor/test' \\"
echo "     -m '{\"device_id\":\"test\",\"temperatura\":65,\"luz\":900,\"humedad\":25}'"
echo ""
