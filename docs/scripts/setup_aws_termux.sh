#!/data/data/com.termux/files/usr/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🔑 CONFIGURACIÓN AWS CREDENTIALS - TERMUX               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Crear directorio .aws si no existe
mkdir -p ~/.aws

# Solicitar credenciales
echo "Necesitas las credenciales AWS del usuario IAM"
echo ""
read -p "AWS Access Key ID: " aws_key
read -p "AWS Secret Access Key: " aws_secret

# Crear archivo credentials
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $aws_key
aws_secret_access_key = $aws_secret
EOF

# Crear archivo config
cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF

chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config

echo ""
echo "✅ Credenciales AWS configuradas"
echo "   ~/.aws/credentials"
echo "   ~/.aws/config"
echo ""
echo "Puedes probar con:"
echo "  python -c \"import boto3; print(boto3.client('s3').list_buckets())\""
echo ""
