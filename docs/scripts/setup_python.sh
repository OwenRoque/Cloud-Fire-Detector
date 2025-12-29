#!/bin/bash
# ============================================================================
# Setup Python Environment - Cloud Fire Detector
# ============================================================================
# Script para crear entorno virtual e instalar dependencias Python
# Ejecutar: ./setup_python.sh
# ============================================================================

set -e

echo "🐍 Cloud Fire Detector - Setup Python"
echo "======================================"
echo ""

# Directorio base
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# 1. Verificar Python
# ============================================================================
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "   Instalar con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION detectado"
echo ""

# ============================================================================
# 2. Crear entorno virtual
# ============================================================================
if [ -d "${PROJECT_DIR}/.venv" ]; then
    echo "📦 Entorno virtual ya existe en .venv/"
    read -p "¿Deseas recrearlo? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "🗑️  Eliminando entorno virtual anterior..."
        rm -rf "${PROJECT_DIR}/.venv"
    else
        echo "✅ Usando entorno virtual existente"
    fi
fi

if [ ! -d "${PROJECT_DIR}/.venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv "${PROJECT_DIR}/.venv"
    echo "✅ Entorno virtual creado en .venv/"
fi

# ============================================================================
# 3. Activar entorno virtual
# ============================================================================
echo ""
echo "🔌 Activando entorno virtual..."
source "${PROJECT_DIR}/.venv/bin/activate"

# ============================================================================
# 4. Actualizar pip
# ============================================================================
echo ""
echo "📥 Actualizando pip..."
pip install --upgrade pip

# ============================================================================
# 5. Instalar dependencias del Fog
# ============================================================================
echo ""
echo "📦 Instalando dependencias del Fog Layer..."
cd "${PROJECT_DIR}/fog"
pip install -r requirements.txt
echo "✅ Dependencias del Fog instaladas"

# ============================================================================
# 6. Instalar dependencias del Edge
# ============================================================================
echo ""
echo "📦 Instalando dependencias del Edge Layer..."
cd "${PROJECT_DIR}/edge"
pip install -r requirements.txt
echo "✅ Dependencias del Edge instaladas"

# ============================================================================
# 7. Volver al directorio raíz
# ============================================================================
cd "${PROJECT_DIR}"

# ============================================================================
# 8. Verificar instalación de AWS IoT SDK (condicional)
# ============================================================================
echo ""
echo "🔍 Verificando AWS IoT SDK..."
if [ -f "${PROJECT_DIR}/fog/certs/certificate.pem.crt" ]; then
    echo "✅ Certificados AWS IoT encontrados"
    echo "📦 Instalando AWS IoT SDK..."
    pip install awsiotsdk==1.12.0
    echo "✅ AWS IoT SDK instalado"
else
    echo "⚠️  Certificados AWS IoT NO encontrados"
    echo "   El fog processor funcionará en MODO LOCAL (sin conexión a AWS)"
    echo "   Si necesitas AWS IoT, ejecuta terraform apply primero"
fi

# ============================================================================
# 9. Crear script de activación rápida
# ============================================================================
echo ""
echo "📝 Creando script de activación..."
cat > "${PROJECT_DIR}/activate.sh" << 'EOF'
#!/bin/bash
# Activar entorno virtual rápidamente
source .venv/bin/activate
echo "✅ Entorno virtual activado"
echo "   Para desactivar: deactivate"
EOF
chmod +x "${PROJECT_DIR}/activate.sh"

# ============================================================================
# 10. Resumen final
# ============================================================================
echo ""
echo "=========================================="
echo "✅ Setup Python completado"
echo "=========================================="
echo ""
echo "📋 Paquetes instalados:"
pip list | grep -E "paho-mqtt|requests|flask|opencv-python|awsiot" || true
echo ""
echo "📋 Para trabajar con el proyecto:"
echo "   1. Activar entorno virtual:"
echo "      source .venv/bin/activate"
echo "      # o simplemente:"
echo "      source activate.sh"
echo ""
echo "   2. Desactivar cuando termines:"
echo "      deactivate"
echo ""
echo "📋 Siguiente paso:"
echo "   Ejecutar: ./start_project.sh"
echo ""
