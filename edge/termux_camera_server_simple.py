#!/usr/bin/env python3
"""
Servidor de Cámara SIMPLIFICADO (sin OpenCV) - Fire Detection System
"""

from flask import Flask, request, jsonify
import subprocess
import os
import random
from datetime import datetime
import logging
import base64

app = Flask(__name__)
SERVER_PORT = 5000
IMAGE_DIR = os.path.expanduser("~/fire_detection_images")
os.makedirs(IMAGE_DIR, exist_ok=True)
CAMERA_ID = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CameraServer")

def capture_photo():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_DIR, f"capture_{timestamp}.jpg")
    try:
        cmd = ["termux-camera-photo", "-c", str(CAMERA_ID), image_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and os.path.exists(image_path):
            logger.info(f" Foto capturada: {image_path}")
            return image_path
        return None
    except Exception as e:
        logger.error(f" Error: {e}")
        return None

def image_to_base64(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.info(f" Imagen codificada ({len(encoded)} chars)")
            return encoded
    except Exception as e:
        logger.error(f" Error: {e}")
        return None

def detect_fire_simple(image_path, sensor_data):
    temp = sensor_data.get("temperatura", 25)
    luz = sensor_data.get("luz", 300)
    fire_score = 0
    if temp > 60:
        fire_score += 0.6
    if luz > 800:
        fire_score += 0.6
    fire_score += random.uniform(0.0, 0.1)
    fire_score = max(0.0, min(1.0, fire_score))
    fire_detected = fire_score > 0.5
    logger.info(f" Análisis: score={fire_score:.2f}")
    return fire_detected, fire_score

@app.route('/')
def index():
    return jsonify({"service": "Fire Detection Camera Server", "status": "running"})

@app.route('/status')
def status():
    return jsonify({"status": "online", "camera_id": CAMERA_ID})

@app.route('/capturar', methods=['POST'])
def capturar():
    try:
        data = request.get_json() or {}
        sensor_id = data.get("sensor_id", "unknown")
        zona = data.get("zona", "unknown")
        logger.info(f" Solicitud de {sensor_id} (zona: {zona})")
        image_path = capture_photo()
        if not image_path:
            return jsonify({"error": "No se pudo capturar", "fire_detected": False, "confidence": 0.0}), 500
        fire_detected, confidence = detect_fire_simple(image_path, data)
        result = {
            "fire_detected": fire_detected,
            "confidence": round(confidence, 3),
            "timestamp": datetime.now().isoformat(),
            "sensor_id": sensor_id,
            "zona": zona,
            "method": "simple"
        }
        if fire_detected:
            logger.warning(f" FUEGO DETECTADO ({confidence:.1%})")
            image_base64 = image_to_base64(image_path)
            if image_base64:
                result["image_data"] = image_base64
                result["image_format"] = "jpeg"
                logger.info(" Imagen incluida")
        else:
            logger.info(f" No fuego ({confidence:.1%})")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f" Error: {e}")
        return jsonify({"error": str(e), "fire_detected": False, "confidence": 0.0}), 500

@app.route('/test')
def test():
    return jsonify({"message": "OK"})

if __name__ == '__main__':
    print(" Servidor de Cámara - Puerto", SERVER_PORT)
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True)
