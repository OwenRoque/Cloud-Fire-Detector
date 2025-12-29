#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🌫️  INICIANDO SISTEMA FOG - FIRE DETECTION             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# Activar entorno virtual
source .venv/bin/activate

# Crear directorio de logs
mkdir -p logs

echo "📋 COMPONENTES DEL SISTEMA:"
echo "  ✅ Mosquitto MQTT (puerto 1883)"
echo "  ✅ Arduino MKR WiFi 1010 (sensor-zona1)"
echo "  🔧 Sensores virtuales (opcional)"
echo "  📸 Cámara Termux (192.168.1.105:5000)"
echo ""

# Preguntar si quiere sensores virtuales
read -p "¿Iniciar sensores virtuales también? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando sensores virtuales..."
    nohup python3 edge/sensores_virtuales.py > logs/sensores_virtuales.log 2>&1 &
    VIRTUAL_PID=$!
    echo "  ✅ Sensores virtuales corriendo (PID: $VIRTUAL_PID)"
    echo ""
fi

echo "🚀 Iniciando Fog Processor..."
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Presiona Ctrl+C para detener"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Ejecutar fog processor en primer plano
python3 fog/fog_processor.py

# Cleanup al salir
if [ ! -z "$VIRTUAL_PID" ]; then
    echo "🛑 Deteniendo sensores virtuales..."
    kill $VIRTUAL_PID 2>/dev/null
fi

echo "✅ Sistema detenido"
