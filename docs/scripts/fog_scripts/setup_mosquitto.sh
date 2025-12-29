#!/bin/bash
# ============================================================================
# Instalación y Configuración de Mosquitto MQTT Broker
# ============================================================================
# Ejecutar en Laptop B (Fog Node)
# Este broker actuará como hub central para todos los sensores locales
# ============================================================================

set -e

echo "🦟 Instalando Mosquitto MQTT Broker..."
echo ""

# Detectar sistema operativo
if [[ -f /etc/debian_version ]]; then
    echo "Sistema: Debian/Ubuntu detectado"
    sudo apt update
    sudo apt install -y mosquitto mosquitto-clients
elif [[ -f /etc/redhat-release ]]; then
    echo "Sistema: RedHat/CentOS detectado"
    sudo yum install -y mosquitto mosquitto-clients
else
    echo "⚠️  Sistema no reconocido. Instala Mosquitto manualmente."
    exit 1
fi

echo ""
echo "📝 Configurando Mosquitto..."

# Detener servicio antes de configurar
sudo systemctl stop mosquitto || true

# Backup de configuración original
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup 2>/dev/null || true

# Crear directorio de configuración si no existe
sudo mkdir -p /etc/mosquitto/conf.d

# Crear configuración personalizada (CORREGIDA - sin duplicados)
sudo tee /etc/mosquitto/conf.d/fog_node.conf > /dev/null <<'EOF'
# ============================================================================
# Configuración Mosquitto - Fire Detection System (Fog Node)
# ============================================================================

# Escuchar en todas las interfaces en puerto 1883 (no cifrado, red local)
listener 1883 0.0.0.0

# Permitir conexiones anónimas (solo para red local confiable)
allow_anonymous true

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information

# Persistencia de mensajes
persistence true
persistence_location /var/lib/mosquitto/

# Limpieza de clientes inactivos
persistent_client_expiration 1d

# Heartbeat
max_keepalive 300

# Límites de memoria
max_queued_messages 1000
message_size_limit 8192
EOF

echo "✅ Configuración creada en /etc/mosquitto/conf.d/fog_node.conf"
echo ""

# Verificar que el archivo principal incluye conf.d
if ! grep -q "include_dir /etc/mosquitto/conf.d" /etc/mosquitto/mosquitto.conf 2>/dev/null; then
    echo "📝 Agregando include_dir a mosquitto.conf..."
    echo "include_dir /etc/mosquitto/conf.d" | sudo tee -a /etc/mosquitto/mosquitto.conf > /dev/null
fi

# Crear directorio de logs si no existe
sudo mkdir -p /var/log/mosquitto
sudo chown mosquitto:mosquitto /var/log/mosquitto

# Verificar permisos de persistencia
sudo chown -R mosquitto:mosquitto /var/lib/mosquitto/

# Validar configuración antes de iniciar
echo "🔍 Validando configuración..."
if ! sudo mosquitto -c /etc/mosquitto/mosquitto.conf -t 2>&1 | grep -q "Error"; then
    echo "✅ Configuración válida"
else
    echo "❌ Error en configuración. Mostrando detalles:"
    sudo mosquitto -c /etc/mosquitto/mosquitto.conf -t
    exit 1
fi

# Reiniciar Mosquitto
echo ""
echo "🔄 Iniciando Mosquitto..."
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Esperar a que inicie
sleep 2

# Verificar estado
echo ""
echo "📊 Estado del servicio:"
if sudo systemctl is-active --quiet mosquitto; then
    echo "✅ Mosquitto está corriendo"
    sudo systemctl status mosquitto --no-pager | head -10
else
    echo "❌ Mosquitto falló al iniciar. Diagnóstico:"
    echo ""
    echo "--- Últimas líneas del log ---"
    sudo journalctl -xeu mosquitto.service --no-pager | tail -20
    echo ""
    echo "--- Log de Mosquitto ---"
    sudo tail -20 /var/log/mosquitto/mosquitto.log 2>/dev/null || echo "Log no disponible"
    exit 1
fi

echo ""

# Obtener IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 Broker MQTT disponible en:"
echo "   mqtt://${LOCAL_IP}:1883"
echo ""

# Prueba rápida
echo "🧪 Probando conexión local..."
timeout 3 mosquitto_sub -h localhost -t "test/ping" -C 1 &
SUB_PID=$!
sleep 1
mosquitto_pub -h localhost -t "test/ping" -m "Hello from Fog Node"
wait $SUB_PID 2>/dev/null || true

echo ""
echo "✅ Mosquitto está funcionando correctamente"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Configurar fog_processor.py con IP: ${LOCAL_IP}"
echo "   2. Actualizar Arduino con broker: ${LOCAL_IP}"
echo "   3. Actualizar sensores virtuales con IP: ${LOCAL_IP}"
echo ""
echo "🔧 Comandos útiles:"
echo "   sudo systemctl status mosquitto     # Ver estado"
echo "   sudo tail -f /var/log/mosquitto/mosquitto.log  # Ver logs"
echo "   mosquitto_sub -h localhost -t '#' -v  # Escuchar todos los tópicos"
echo ""