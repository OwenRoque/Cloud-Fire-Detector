variable "project_name" {
  default     = "fire-detection"
  description = "Nombre base del proyecto"
}

variable "aws_region" {
  default     = "us-east-1"
  description = "Región AWS principal"
}

# ============================================================================
# Configuración Fog Computing - Mapa de Proximidad
# ============================================================================
variable "sensor_camera_map" {
  type        = map(string)
  description = "Mapa de sensores a cámaras (Sensor ID → IP de cámara/celular)"

  default = {
    "sensor-zona1"     = "192.168.1.105" # Arduino MKR WiFi 1010
    "sensor-zona2"     = "192.168.1.105" # Reutiliza misma cámara
    "sensor-virtual-1" = "192.168.1.105" # Sensores virtuales (Laptop A)
    "sensor-virtual-2" = "192.168.1.105"
    "sensor-virtual-3" = "192.168.1.105"
    "sensor-virtual-4" = "192.168.1.105"
    "sensor-virtual-5" = "192.168.1.105"
  }
}

variable "fog_mqtt_broker_ip" {
  type        = string
  description = "IP del bróker MQTT local (Laptop B - Nodo Fog)"
  default     = "192.168.1.100" # ⚠️ CAMBIAR A LA IP REAL DE TU LAPTOP B
}

# ============================================================================
# Telegram Bot (Notificaciones)
# ============================================================================
variable "telegram_bot_token" {
  type        = string
  description = "Token del Bot de Telegram para alertas"
  sensitive   = true
  default     = "PUT_YOUR_TOKEN_HERE" # Reemplazar con token real
}

variable "telegram_chat_id" {
  type        = string
  description = "Chat ID de Telegram donde se enviarán las alertas"
  sensitive   = true
  default     = "PUT_YOUR_CHAT_ID" # Reemplazar con chat ID real
}
