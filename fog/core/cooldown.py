import time
from config.settings import ALERT_COOLDOWN

_last_alert_time = {}

def is_in_cooldown(sensor_id: str) -> bool:
    if sensor_id in _last_alert_time:
        return (time.time() - _last_alert_time[sensor_id]) < ALERT_COOLDOWN
    return False

def update_cooldown(sensor_id: str):
    _last_alert_time[sensor_id] = time.time()
