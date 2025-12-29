#!/bin/bash
# ============================================================================
# Continue Setup - AWS IoT Configuration
# ============================================================================
# Ejecutar DESPUÉS de configurar credenciales AWS
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Continuando configuración AWS IoT...                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Verificar credenciales AWS
echo "🔍 Verificando credenciales AWS..."
if aws sts get-caller-identity &>/dev/null; then
    echo "✅ Credenciales AWS configuradas correctamente"
    aws sts get-caller-identity
    echo ""
else
    echo "❌ Error: Credenciales AWS no válidas"
    echo "   Ejecuta: aws configure"
    exit 1
fi

# Terraform Init
echo "╔════════════════════════════════════════════════════════╗"
echo "║  PASO 4: Inicializando Terraform                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

terraform init

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  PASO 5: Desplegando infraestructura AWS               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  Esto creará los siguientes recursos en AWS:"
echo "   • IoT Core Thing + Certificados"
echo "   • Lambda Function (fire_handler)"
echo "   • DynamoDB Table"
echo "   • SNS Topic"
echo "   • S3 Bucket"
echo "   • IAM Roles y Policies"
echo ""
read -p "¿Continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Cancelado por el usuario"
    exit 1
fi

# Terraform Apply
terraform apply -auto-approve

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  PASO 6: Extrayendo certificados IoT                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Ejecutar script de extracción de certificados
if [ -f "extract_certs.sh" ]; then
    chmod +x extract_certs.sh
    ./extract_certs.sh
else
    echo "⚠️  Script extract_certs.sh no encontrado"
    echo "   Creando certificados manualmente..."
    
    # Crear directorio de certificados
    mkdir -p fog/certs
    
    # Extraer certificados del terraform output
    terraform output -raw iot_certificate_pem > fog/certs/certificate.pem.crt
    terraform output -raw iot_private_key > fog/certs/private.pem.key
    
    # Descargar Amazon Root CA
    curl -o fog/certs/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
    
    echo "✅ Certificados creados en fog/certs/"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  PASO 7: Actualizando configuración del Fog            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Obtener IoT Endpoint
IOT_ENDPOINT=$(terraform output -raw iot_endpoint)
echo "📡 IoT Endpoint: $IOT_ENDPOINT"

# Actualizar fog/config/settings.py con el endpoint
if [ -f "fog/config/settings.py" ]; then
    # Crear backup
    cp fog/config/settings.py fog/config/settings.py.backup
    
    # Actualizar endpoint
    sed -i "s|AWS_IOT_ENDPOINT = \".*\"|AWS_IOT_ENDPOINT = \"$IOT_ENDPOINT\"|g" fog/config/settings.py
    
    echo "✅ Configuración actualizada en fog/config/settings.py"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  PASO 8: Instalando AWS IoT SDK                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

./setup_python.sh

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ CONFIGURACIÓN COMPLETADA                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Recursos creados en AWS:"
terraform output -json | jq -r 'keys[]' | sed 's/^/   • /'
echo ""
echo "📋 Certificados IoT:"
ls -lh fog/certs/
echo ""
echo "📋 Siguiente paso:"
echo "   ./start_project.sh"
echo ""
echo "🌐 El Fog Processor ahora enviará alertas a AWS IoT Core"
echo ""
