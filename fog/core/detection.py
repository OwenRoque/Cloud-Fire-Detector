from config.settings import THRESHOLDS

def analyze(sensor_data: dict) -> dict:
    temperatura = sensor_data.get("temperatura", 0)
    luz = sensor_data.get("luz", 0)
    humedad = sensor_data.get("humedad", 100)

    return {
        "temp_critical": temperatura > THRESHOLDS["temperatura"],
        "luz_critical": luz > THRESHOLDS["luz"],
        "humedad_critical": humedad < THRESHOLDS["humedad"],
        "temperatura": temperatura,
        "luz": luz,
        "humedad": humedad
    }
