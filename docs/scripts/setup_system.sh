#!/bin/bash
# ============================================================================
# Setup System - Cloud Fire Detector
# ============================================================================
# Script para instalar dependencias del sistema (Mosquitto, etc.)
# Ejecutar: sudo ./setup_system.sh
# ============================================================================

set -e

echo "🔥 Cloud Fire Detector - Setup del Sistema"
echo "=========================================="
echo ""

# Verificar si se ejecuta con sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script debe ejecutarse con sudo"
    echo "   Ejecutar: sudo ./setup_system.sh"
    exit 1
fi

# ============================================================================
# 1. Actualizar repositorios
# ============================================================================
echo "📦 Actualizando repositorios..."
apt update

# ============================================================================
# 2. Instalar Mosquitto MQTT Broker
# ============================================================================
echo ""
echo "🦟 Instalando Mosquitto MQTT Broker..."
apt install -y mosquitto mosquitto-clients

# ============================================================================
# 3. Configurar Mosquitto
# ============================================================================
echo ""
echo "⚙️  Configurando Mosquitto..."

# Backup de configuración original si existe
if [ -f /etc/mosquitto/mosquitto.conf ]; then
    cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup
fi

# Crear configuración personalizada
cat > /etc/mosquitto/conf.d/fire-detector.conf << EOF
# Cloud Fire Detector - MQTT Configuration
listener 1883
allow_anonymous true
bind_address 0.0.0.0

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_timestamp true
EOF

# ============================================================================
# 4. Habilitar y reiniciar Mosquitto
# ============================================================================
echo ""
echo "🔄 Habilitando Mosquitto..."
systemctl enable mosquitto
systemctl restart mosquitto

# Verificar estado
sleep 2
if systemctl is-active --quiet mosquitto; then
    echo "✅ Mosquitto está corriendo correctamente"
else
    echo "❌ Error: Mosquitto no está corriendo"
    echo "   Verificar con: sudo systemctl status mosquitto"
    exit 1
fi

# ============================================================================
# 5. Verificar puerto 1883
# ============================================================================
echo ""
echo "🔍 Verificando puerto 1883..."
if netstat -tuln | grep -q ':1883'; then
    echo "✅ Puerto 1883 está abierto"
else
    echo "⚠️  Advertencia: Puerto 1883 no está escuchando"
fi

# ============================================================================
# 6. Mostrar información del usuario actual
# ============================================================================
REAL_USER="${SUDO_USER:-$USER}"
echo ""
echo "=========================================="
echo "✅ Instalación del sistema completada"
echo "=========================================="
echo ""
echo "📋 Siguiente paso:"
echo "   1. Salir de sudo (ya no es necesario)"
echo "   2. Como usuario normal '$REAL_USER', ejecutar:"
echo "      ./setup_python.sh"
echo ""
echo "🦟 Estado de Mosquitto:"
echo "   - Puerto: 1883"
echo "   - Comandos útiles:"
echo "     sudo systemctl status mosquitto   # Ver estado"
echo "     sudo systemctl restart mosquitto  # Reiniciar"
echo "     mosquitto_sub -h localhost -t '#' -v  # Monitorear mensajes"
echo ""
