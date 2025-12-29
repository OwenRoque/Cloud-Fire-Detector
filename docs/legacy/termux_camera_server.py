#!/usr/bin/env python3
"""
Servidor de Cámara - Fire Detection System (Termux)
Universidad Nacional de San Agustín - Arequipa, Perú

Servidor Flask que corre en Termux (Android) para:
1. Recibir solicitudes del Fog Node
2. Capturar foto usando termux-camera-photo
3. Detectar fuego usando OpenCV (análisis HSV + contornos)
4. Devolver resultado JSON: {"fire_detected": bool, "confidence": float}

INSTALACIÓN EN TERMUX:
1. pkg update && pkg upgrade
2. pkg install python opencv termux-api
3. pip install flask pillow numpy opencv-python
4. Dar permisos de cámara a Termux:API en Android

EJECUCIÓN:
python3 termux_camera_server.py
"""

from flask import Flask, request, jsonify
import subprocess
import os
import cv2
import numpy as np
from datetime import datetime
import json
import logging

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

app = Flask(__name__)

# Puerto del servidor
SERVER_PORT = 5000

# Directorio para imágenes capturadas
IMAGE_DIR = os.path.expanduser("~/fire_detection_images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# Cámara a usar (0=trasera, 1=frontal)
CAMERA_ID = 0

# Umbrales para detección de fuego (HSV)
# Rango de color naranja-rojo-amarillo (fuego)
FIRE_HSV_LOWER = np.array([10, 100, 100])  # Hue mínimo, Sat mínima, Value mínimo
FIRE_HSV_UPPER = np.array([35, 255, 255])  # Hue máximo, Sat máxima, Value máximo

# Área mínima de contorno para considerar fuego (píxeles)
MIN_FIRE_AREA = 500

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CameraServer")

# ============================================================================
# FUNCIONES DE DETECCIÓN
# ============================================================================

def capture_photo():
    """Captura una foto usando termux-camera-photo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_DIR, f"capture_{timestamp}.jpg")
    
    try:
        # Comando Termux para capturar foto
        cmd = [
            "termux-camera-photo",
            "-c", str(CAMERA_ID),
            image_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and os.path.exists(image_path):
            logger.info(f"📷 Foto capturada: {image_path}")
            return image_path
        else:
            logger.error(f"❌ Error al capturar: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("⏱️  Timeout al capturar foto")
        return None
    except Exception as e:
        logger.error(f"❌ Excepción al capturar: {e}")
        return None

def detect_fire_opencv(image_path):
    """Detecta fuego en imagen usando OpenCV (análisis HSV)"""
    try:
        # Leer imagen
        img = cv2.imread(image_path)
        if img is None:
            logger.error("❌ No se pudo leer la imagen")
            return False, 0.0
        
        # Convertir a HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Máscara para detectar colores de fuego (naranja-amarillo-rojo)
        mask = cv2.inRange(hsv, FIRE_HSV_LOWER, FIRE_HSV_UPPER)
        
        # Operaciones morfológicas para reducir ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analizar contornos
        fire_contours = []
        total_fire_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_FIRE_AREA:
                fire_contours.append(contour)
                total_fire_area += area
        
        # Calcular confianza basada en área total
        image_area = img.shape[0] * img.shape[1]
        fire_percentage = (total_fire_area / image_area) * 100
        
        # Determinar si hay fuego
        fire_detected = len(fire_contours) > 0 and fire_percentage > 0.5
        
        # Confianza (0.0 - 1.0)
        confidence = min(fire_percentage / 10.0, 1.0)  # Normalizar a 0-1
        
        logger.info(f"   Contornos detectados: {len(fire_contours)}")
        logger.info(f"   Área de fuego: {fire_percentage:.2f}%")
        logger.info(f"   Confianza: {confidence:.2%}")
        
        # Guardar imagen con detecciones (opcional para debug)
        if fire_detected:
            debug_img = img.copy()
            cv2.drawContours(debug_img, fire_contours, -1, (0, 255, 0), 2)
            debug_path = image_path.replace(".jpg", "_detected.jpg")
            cv2.imwrite(debug_path, debug_img)
            logger.info(f"   Debug image saved: {debug_path}")
        
        return fire_detected, confidence
        
    except Exception as e:
        logger.error(f"❌ Error en detección OpenCV: {e}")
        return False, 0.0

# ============================================================================
# ENDPOINTS FLASK
# ============================================================================

@app.route('/')
def index():
    """Endpoint de status"""
    return jsonify({
        "service": "Fire Detection Camera Server",
        "status": "running",
        "university": "UNSA - Arequipa, Perú",
        "endpoints": {
            "/capturar": "POST - Captura foto y detecta fuego",
            "/status": "GET - Estado del servidor"
        }
    })

@app.route('/status')
def status():
    """Estado del servidor"""
    return jsonify({
        "status": "online",
        "camera_id": CAMERA_ID,
        "image_dir": IMAGE_DIR,
        "images_captured": len([f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')])
    })

@app.route('/capturar', methods=['POST'])
def capturar():
    """
    Endpoint principal: captura foto y detecta fuego
    
    Request JSON (opcional):
    {
        "sensor_id": "sensor-zona1",
        "zona": "zona1",
        "temperatura": 65.0,
        "luz": 900
    }
    
    Response JSON:
    {
        "fire_detected": true,
        "confidence": 0.85,
        "timestamp": "2025-12-28T10:30:00",
        "image_path": "/path/to/image.jpg",
        "sensor_id": "sensor-zona1"
    }
    """
    try:
        # Obtener datos de la solicitud
        data = request.get_json() or {}
        sensor_id = data.get("sensor_id", "unknown")
        zona = data.get("zona", "unknown")
        
        logger.info(f"📸 Solicitud de captura desde {sensor_id} (zona: {zona})")
        
        # Capturar foto
        image_path = capture_photo()
        
        if not image_path:
            return jsonify({
                "error": "No se pudo capturar la foto",
                "fire_detected": False,
                "confidence": 0.0
            }), 500
        
        # Detectar fuego
        logger.info("🔍 Analizando imagen con OpenCV...")
        fire_detected, confidence = detect_fire_opencv(image_path)
        
        # Resultado
        result = {
            "fire_detected": fire_detected,
            "confidence": round(confidence, 3),
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "sensor_id": sensor_id,
            "zona": zona,
            "camera_id": CAMERA_ID
        }
        
        if fire_detected:
            logger.warning(f"🔥 FUEGO DETECTADO (confianza: {confidence:.1%})")
        else:
            logger.info(f"✅ No se detectó fuego (confianza: {confidence:.1%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"❌ Error en /capturar: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "fire_detected": False,
            "confidence": 0.0
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Endpoint de prueba sin captura real"""
    logger.info("🧪 Test endpoint llamado")
    return jsonify({
        "message": "Camera server is working!",
        "test_mode": True,
        "fire_detected": False,
        "confidence": 0.0
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("📷 SERVIDOR DE CÁMARA - Fire Detection System")
    print("   Universidad Nacional de San Agustín - Arequipa, Perú")
    print("=" * 70)
    print()
    print(f"🌐 Servidor Flask iniciando en puerto {SERVER_PORT}...")
    print(f"📁 Imágenes se guardarán en: {IMAGE_DIR}")
    print(f"📸 Usando cámara ID: {CAMERA_ID} (0=trasera, 1=frontal)")
    print()
    print("📋 Endpoints disponibles:")
    print(f"   http://0.0.0.0:{SERVER_PORT}/")
    print(f"   http://0.0.0.0:{SERVER_PORT}/status")
    print(f"   http://0.0.0.0:{SERVER_PORT}/capturar (POST)")
    print(f"   http://0.0.0.0:{SERVER_PORT}/test")
    print()
    print("⚠️  IMPORTANTE: Asegúrate de que Termux:API tenga permisos de cámara")
    print()
    
    # Iniciar servidor Flask
    # Escuchar en todas las interfaces (0.0.0.0) para permitir conexiones externas
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True)
