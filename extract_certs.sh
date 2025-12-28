#!/bin/bash
# ============================================================================
# Script de Extracción de Certificados IoT Core
# ============================================================================
# Ejecutar DESPUÉS de `terraform apply`
# Guarda los certificados X.509 necesarios para el Fog Node
# ============================================================================

set -e

echo "🔐 Extrayendo certificados de AWS IoT Core..."
echo ""

# Directorio para certificados
CERT_DIR="./fog/certs"
mkdir -p "$CERT_DIR"

# Extraer certificados usando terraform output
echo "📄 Guardando certificate.pem.crt..."
terraform output -raw iot_certificate_pem > "$CERT_DIR/certificate.pem.crt"

echo "🔑 Guardando private.pem.key..."
terraform output -raw iot_private_key > "$CERT_DIR/private.pem.key"

echo "🔓 Guardando public.pem.key..."
terraform output -raw iot_public_key > "$CERT_DIR/public.pem.key"

# Descargar Amazon Root CA1
echo "📥 Descargando Amazon Root CA1..."
curl -o "$CERT_DIR/AmazonRootCA1.pem" https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Permisos restrictivos
chmod 600 "$CERT_DIR"/*.key
chmod 644 "$CERT_DIR"/*.crt
chmod 644 "$CERT_DIR"/*.pem

echo ""
echo "✅ Certificados guardados en: $CERT_DIR/"
echo ""
echo "📋 Contenido del directorio:"
ls -lh "$CERT_DIR"
echo ""
echo "🔍 Endpoint de AWS IoT Core:"
terraform output -raw iot_endpoint
echo ""
