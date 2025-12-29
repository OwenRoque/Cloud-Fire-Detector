#!/bin/bash
# ============================================================================
# Start Cloud Fire Detector Project
# ============================================================================
# Script para iniciar todos los componentes del sistema
# Ejecutar: ./start_project.sh
# ============================================================================

set -e

# Directorio base
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# Funciones
# ============================================================================

check_mosquitto() {
    if ! systemctl is-active --quiet mosquitto; then
        echo "❌ Mosquitto no está corriendo"
        echo "   Iniciar con: sudo systemctl start mosquitto"
        exit 1
    fi
    echo "✅ Mosquitto está corriendo"
}

check_venv() {
    if [ ! -d "${PROJECT_DIR}/.venv" ]; then
        echo "❌ Entorno virtual no encontrado"
        echo "   Ejecutar primero: ./setup_python.sh"
        exit 1
    fi
    echo "✅ Entorno virtual encontrado"
}

start_sensores() {
    echo ""
    echo "📡 Iniciando sensores virtuales..."
    echo "   Ejecutando: python3 edge/sensores_virtuales.py"
    echo "   (Presiona Ctrl+C para detener)"
    echo ""
    cd "${PROJECT_DIR}"
    source .venv/bin/activate
    python3 edge/sensores_virtuales.py
}

start_fog() {
    echo ""
    echo "🌫️  Iniciando Fog Processor..."
    echo "   Ejecutando: python3 fog/fog_processor.py"
    echo "   (Presiona Ctrl+C para detener)"
    echo ""
    cd "${PROJECT_DIR}"
    source .venv/bin/activate
    python3 fog/fog_processor.py
}

show_menu() {
    echo "🔥 Cloud Fire Detector - Menú de Inicio"
    echo "========================================"
    echo ""
    echo "Selecciona qué componente iniciar:"
    echo ""
    echo "  1) Sensores Virtuales (edge/sensores_virtuales.py)"
    echo "  2) Fog Processor (fog/fog_processor.py)"
    echo "  3) Ambos (en terminales separadas - recomendado)"
    echo "  4) Verificar estado del sistema"
    echo "  5) Salir"
    echo ""
}

verify_system() {
    echo ""
    echo "🔍 Verificando estado del sistema..."
    echo "========================================"
    echo ""
    
    # Mosquitto
    echo "🦟 Mosquitto MQTT Broker:"
    if systemctl is-active --quiet mosquitto; then
        echo "   ✅ Estado: Activo"
        echo "   📡 Puerto: 1883"
    else
        echo "   ❌ Estado: Inactivo"
        echo "   💡 Iniciar con: sudo systemctl start mosquitto"
    fi
    
    # Entorno virtual
    echo ""
    echo "🐍 Entorno Virtual Python:"
    if [ -d "${PROJECT_DIR}/.venv" ]; then
        echo "   ✅ Estado: Creado"
        source .venv/bin/activate
        echo "   📦 Paquetes principales:"
        pip list | grep -E "paho-mqtt|requests|awsiot" | sed 's/^/      /' || echo "      (instalando...)"
        deactivate
    else
        echo "   ❌ Estado: No creado"
        echo "   💡 Crear con: ./setup_python.sh"
    fi
    
    # Certificados AWS IoT
    echo ""
    echo "🔐 Certificados AWS IoT:"
    if [ -f "${PROJECT_DIR}/fog/certs/certificate.pem.crt" ]; then
        echo "   ✅ Estado: Encontrados"
        echo "   ☁️  Modo: Cloud habilitado"
    else
        echo "   ⚠️  Estado: No encontrados"
        echo "   🏝️  Modo: Solo local (modo isla)"
    fi
    
    # Configuración
    echo ""
    echo "⚙️  Configuración:"
    if [ -f "${PROJECT_DIR}/fog/config/settings.py" ]; then
        echo "   ✅ settings.py existe"
        source .venv/bin/activate 2>/dev/null
        AWS_STATUS=$(python3 -c "from fog.config.settings import AWS_IOT_ENABLED; print('Habilitado' if AWS_IOT_ENABLED else 'Deshabilitado')" 2>/dev/null || echo "Error")
        deactivate 2>/dev/null
        echo "   ☁️  AWS IoT: $AWS_STATUS"
    fi
    
    echo ""
    echo "========================================"
    echo ""
}

start_both() {
    echo ""
    echo "🚀 Iniciando ambos componentes..."
    echo "========================================"
    echo ""
    echo "Se abrirán DOS terminales nuevas:"
    echo "  Terminal 1: Sensores Virtuales"
    echo "  Terminal 2: Fog Processor"
    echo ""
    echo "⚠️  Orden de inicio:"
    echo "  1. Primero iniciará los sensores (Terminal 1)"
    echo "  2. Espera 5 segundos..."
    echo "  3. Luego iniciará el fog processor (Terminal 2)"
    echo ""
    echo "Para detener: Cierra cada terminal o presiona Ctrl+C en cada una"
    echo ""
    read -p "Presiona Enter para continuar..."
    
    # Detectar terminal disponible
    if command -v gnome-terminal &> /dev/null; then
        TERM_CMD="gnome-terminal"
    elif command -v xterm &> /dev/null; then
        TERM_CMD="xterm -e"
    elif command -v konsole &> /dev/null; then
        TERM_CMD="konsole -e"
    else
        echo "❌ No se encontró un emulador de terminal compatible"
        echo "   Abre dos terminales manualmente y ejecuta:"
        echo "   Terminal 1: ./start_project.sh (opción 1)"
        echo "   Terminal 2: ./start_project.sh (opción 2)"
        exit 1
    fi
    
    # Iniciar sensores
    echo "📡 Iniciando Terminal 1: Sensores..."
    $TERM_CMD bash -c "cd '$PROJECT_DIR' && source .venv/bin/activate && echo '📡 Sensores Virtuales' && echo '=====================' && echo '' && python3 edge/sensores_virtuales.py; exec bash" &
    
    # Esperar un momento
    sleep 3
    
    # Iniciar fog processor
    echo "🌫️  Iniciando Terminal 2: Fog Processor..."
    $TERM_CMD bash -c "cd '$PROJECT_DIR' && source .venv/bin/activate && echo '🌫️  Fog Processor' && echo '=====================' && echo '' && python3 fog/fog_processor.py; exec bash" &
    
    echo ""
    echo "✅ Terminales iniciadas"
    echo ""
    echo "📋 Monitoreo MQTT (opcional):"
    echo "   Abrir otra terminal y ejecutar:"
    echo "   mosquitto_sub -h localhost -t '#' -v"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

echo "🔥 Cloud Fire Detector"
echo "======================================"
echo ""

# Verificaciones iniciales
check_mosquitto
check_venv

# Menú interactivo
while true; do
    show_menu
    read -p "Opción: " choice
    
    case $choice in
        1)
            start_sensores
            ;;
        2)
            start_fog
            ;;
        3)
            start_both
            break
            ;;
        4)
            verify_system
            ;;
        5)
            echo "👋 Saliendo..."
            exit 0
            ;;
        *)
            echo "❌ Opción inválida"
            ;;
    esac
done
