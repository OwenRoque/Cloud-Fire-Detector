#!/usr/bin/env python3
"""
Servidor de Cámara SIMPLIFICADO (sin OpenCV) - Fire Detection System
Para probar el flujo mientras OpenCV se instala

Ejecutar en Termux:
python termux_camera_server_simple.py
"""

from flask import Flask, request, jsonify
import subprocess
import os
import random
from datetime import datetime
import logging

app = Flask(__name__)

# Configuración
SERVER_PORT = 5000
IMAGE_DIR = os.path.expanduser("~/fire_detection_images")
os.makedirs(IMAGE_DIR, exist_ok=True)
CAMERA_ID = 0

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CameraServer")

def capture_photo():
    """Captura foto con termux-camera-photo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_DIR, f"capture_{timestamp}.jpg")
    
    try:
        cmd = ["termux-camera-photo", "-c", str(CAMERA_ID), image_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and os.path.exists(image_path):
            logger.info(f"📷 Foto capturada: {image_path}")
            return image_path
        else:
            logger.error(f"❌ Error al capturar: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

def detect_fire_simple(image_path, sensor_data):
    """
    Detección SIMULADA basada en datos del sensor
    (Reemplazar con OpenCV cuando esté instalado)
    """
    # Lógica simple: si temp > 70 o luz > 850, simular detección
    temp = sensor_data.get("temperatura", 25)
    luz = sensor_data.get("luz", 300)
    
    # Probabilidad de detección basada en valores
    fire_score = 0
    if temp > 70:
        fire_score += 0.4
    if luz > 850:
        fire_score += 0.4
    if temp > 60 and luz > 800:
        fire_score += 0.2
    
    # Agregar algo de aleatoriedad (simular análisis de imagen)
    fire_score += random.uniform(-0.1, 0.1)
    fire_score = max(0.0, min(1.0, fire_score))
    
    fire_detected = fire_score > 0.5
    
    logger.info(f"🔍 Análisis simulado: score={fire_score:.2f}")
    return fire_detected, fire_score

@app.route('/')
def index():
    return jsonify({
        "service": "Fire Detection Camera Server (Simple)",
        "status": "running",
        "note": "OpenCV no instalado - usando detección simulada",
        "endpoints": {
            "/capturar": "POST - Captura foto y detecta fuego",
            "/status": "GET - Estado del servidor"
        }
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "camera_id": CAMERA_ID,
        "opencv_installed": False,
        "image_dir": IMAGE_DIR,
        "images_captured": len([f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')])
    })

@app.route('/capturar', methods=['POST'])
def capturar():
    """Captura foto y detecta fuego (versión simplificada)"""
    try:
        data = request.get_json() or {}
        sensor_id = data.get("sensor_id", "unknown")
        zona = data.get("zona", "unknown")
        
        logger.info(f"📸 Solicitud de {sensor_id} (zona: {zona})")
        
        # Capturar foto
        image_path = capture_photo()
        
        if not image_path:
            return jsonify({
                "error": "No se pudo capturar la foto",
                "fire_detected": False,
                "confidence": 0.0
            }), 500
        
        # Detectar fuego (simulado)
        logger.info("🔍 Analizando con método simplificado...")
        fire_detected, confidence = detect_fire_simple(image_path, data)
        
        result = {
            "fire_detected": fire_detected,
            "confidence": round(confidence, 3),
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "sensor_id": sensor_id,
            "zona": zona,
            "method": "simple",
            "note": "OpenCV pendiente de instalación"
        }
        
        if fire_detected:
            logger.warning(f"🔥 FUEGO DETECTADO (confianza: {confidence:.1%})")
        else:
            logger.info(f"✅ No se detectó fuego (confianza: {confidence:.1%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({
            "error": str(e),
            "fire_detected": False,
            "confidence": 0.0
        }), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Camera server working!",
        "opencv_installed": False
    })

if __name__ == '__main__':
    print("=" * 70)
    print("📷 SERVIDOR DE CÁMARA SIMPLIFICADO")
    print("   (Sin OpenCV - Detección simulada)")
    print("=" * 70)
    print(f"\n🌐 Servidor en puerto {SERVER_PORT}")
    print(f"📁 Imágenes en: {IMAGE_DIR}")
    print(f"📸 Cámara ID: {CAMERA_ID}\n")
    print("⚠️  Instala OpenCV para detección real:")
    print("   pkg install opencv-python")
    print("   O: pip install opencv-python-headless\n")
    
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True)