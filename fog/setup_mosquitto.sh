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

# Backup de configuración original
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup

# Crear configuración personalizada
sudo tee /etc/mosquitto/conf.d/fog_node.conf > /dev/null <<EOF
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
log_type all

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

# Wildcard subscriptions permitidas
allow_anonymous true
EOF

echo "✅ Configuración creada en /etc/mosquitto/conf.d/fog_node.conf"
echo ""

# Reiniciar Mosquitto
echo "🔄 Reiniciando Mosquitto..."
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

echo ""
echo "✅ Mosquitto instalado y corriendo"
echo ""

# Verificar estado
echo "📊 Estado del servicio:"
sudo systemctl status mosquitto --no-pager | head -10
echo ""

# Obtener IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 Broker MQTT disponible en:"
echo "   mqtt://${LOCAL_IP}:1883"
echo ""

# Prueba rápida
echo "🧪 Probando conexión local..."
mosquitto_pub -h localhost -t "test/ping" -m "Hello from Fog Node" &
sleep 1
mosquitto_sub -h localhost -t "test/ping" -C 1

echo ""
echo "✅ Mosquitto está funcionando correctamente"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Configurar fog_processor.py con IP: ${LOCAL_IP}"
echo "   2. Actualizar Arduino con broker: ${LOCAL_IP}"
echo "   3. Actualizar sensores virtuales con IP: ${LOCAL_IP}"
echo ""
