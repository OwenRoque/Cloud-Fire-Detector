variable "sensor_camera_map" {
  type        = map(string)
  description = "Mapa de sensores a cámaras (Sensor ID → IP de cámara/celular)"

  default = {
    "sensor-zona1"     = "192.168.0.41"  # ← Tu teléfono
    "sensor-zona2"     = "192.168.0.41"
    "sensor-virtual-1" = "192.168.0.41"
    "sensor-virtual-2" = "192.168.0.41"
    "sensor-virtual-3" = "192.168.0.41"
    "sensor-virtual-4" = "192.168.0.41"
    "sensor-virtual-5" = "192.168.0.41"
  }
}

variable "fog_mqtt_broker_ip" {
  type        = string
  description = "IP del bróker MQTT local (Laptop B - Nodo Fog)"
  default     = "192.168.0.42"  # ← Tu laptop (Fog Node)
}

variable "telegram_bot_token" {
  type        = string
  description = "Token del Bot de Telegram para alertas"
  sensitive   = true
  default     = "8128198300:AAEWmUMh6EDgU_mqlA7_ML54rw035KG3OlU"
}

variable "telegram_chat_id" {
  type        = string
  description = "Chat ID de Telegram donde se enviarán las alertas"
  sensitive   = true
  default     = "6435171742"
}