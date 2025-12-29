import requests
from config.settings import SENSOR_CAMERA_MAP, CAMERA_PORT, CAMERA_TIMEOUT

def request_confirmation(sensor_id: str, zona: str, data: dict):
    camera_ip = SENSOR_CAMERA_MAP.get(sensor_id)
    if not camera_ip:
        return {"confirmed": False, "confidence": 0.0}

    url = f"http://{camera_ip}:{CAMERA_PORT}/capturar"
    response = requests.post(
        url,
        json={
            "sensor_id": sensor_id,
            "zona": zona,
            "temperatura": data.get("temperatura"),
            "luz": data.get("luz")
        },
        timeout=CAMERA_TIMEOUT
    )

    if response.status_code == 200:
        return response.json()

    raise RuntimeError("Camera error")
