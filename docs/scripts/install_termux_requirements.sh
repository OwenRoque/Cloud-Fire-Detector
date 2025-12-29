#!/data/data/com.termux/files/usr/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  📦 INSTALANDO DEPENDENCIAS TERMUX - FIRE DETECTION      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

echo "🔧 Actualizando paquetes..."
pkg update -y
pkg upgrade -y

echo ""
echo "📦 Instalando Python y dependencias..."
pkg install -y python python-pip termux-api

echo ""
echo "🐍 Instalando librerías Python..."
pip install --upgrade pip
pip install flask boto3 requests

echo ""
echo "✅ INSTALACIÓN COMPLETA"
echo ""
echo "📋 Siguiente paso:"
echo "   1. Ejecutar: python termux_camera_server_simple.py"
echo "   2. Configurar credenciales AWS (si no están):"
echo "      export AWS_ACCESS_KEY_ID=your_key"
echo "      export AWS_SECRET_ACCESS_KEY=your_secret"
echo ""
