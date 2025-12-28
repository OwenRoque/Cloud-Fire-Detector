/*
  Fire Detection System - Arduino MKR WiFi 1010 con MQTT LOCAL
  Universidad Nacional de San Agustín - Arequipa, Perú
  
  ✨ VERSIÓN ACTUALIZADA PARA FOG COMPUTING ✨
  
  Este código lee los sensores del MKR IoT Carrier y envía
  los datos al Fog Node (Laptop B) vía MQTT LOCAL.
  
  ⚠️  CAMBIOS PRINCIPALES:
  - Broker MQTT: HiveMQ Cloud → Laptop B (IP local)
  - Topics: unsa/* → industria/zona1/sensor/arduino
  - Device ID: Identificador único del sensor
  
  Sensores:
  - HTS221: Temperatura y Humedad
  - APDS9960: Luz ambiente (RGB promedio)
  - LPS22HB: Presión barométrica
*/

#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <ArduinoJson.h>
#include <Arduino_MKRIoTCarrier.h>

// ============================================================================
// CONFIGURACIÓN WiFi - MODIFICA ESTOS VALORES
// ============================================================================
const char* ssid = "TU_WIFI_SSID";           // Nombre de tu red WiFi
const char* password = "TU_WIFI_PASSWORD";   // Contraseña de tu WiFi

// ============================================================================
// CONFIGURACIÓN MQTT - FOG NODE (Laptop B)
// ============================================================================
const char* mqtt_broker = "192.168.1.100";  // ⚠️ CAMBIAR A IP DE LAPTOP B
const int mqtt_port = 1883;
const char* mqtt_client_id = "arduino-zona1";  // ID único del cliente

// Topics MQTT locales (compatible con Fog Processor)
const char* mqtt_topic_sensores = "industria/zona1/sensor/arduino";
const char* mqtt_topic_status = "industria/zona1/status";
const char* mqtt_topic_comandos = "industria/zona1/comandos";

// Device ID (debe coincidir con el mapa en fog_config.json)
const char* device_id = "sensor-zona1";

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================
MKRIoTCarrier carrier;
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

unsigned long lastSendTime = 0;
const unsigned long sendInterval = 5000;  // Enviar cada 5 segundos

// ============================================================================
// SETUP - Inicialización
// ============================================================================
void setup() {
  // Iniciar comunicación serial
  Serial.begin(9600);
  while (!Serial && millis() < 5000);  // Esperar 5 segundos máximo
  
  Serial.println("========================================");
  Serial.println("Fire Detection System - FOG COMPUTING");
  Serial.println("UNSA - Arequipa, Peru");
  Serial.println("========================================");
  Serial.println();
  
  // Inicializar MKR IoT Carrier
  Serial.println("Inicializando MKR IoT Carrier...");
  if (!carrier.begin()) {
    Serial.println("ERROR: No se pudo inicializar el Carrier!");
    Serial.println("Verifica que el MKR WiFi 1010 esté en el Carrier");
    while (1);  // Detener ejecución
  }
  Serial.println("✓ Carrier inicializado");
  
  // Mostrar mensaje en pantalla
  carrier.display.fillScreen(0x0000);  // Negro
  carrier.display.setTextColor(0xFFFF); // Blanco
  carrier.display.setTextSize(2);
  carrier.display.setCursor(10, 80);
  carrier.display.print("Fire Detect");
  carrier.display.setCursor(20, 110);
  carrier.display.print("FOG Mode");
  carrier.display.setCursor(30, 140);
  carrier.display.print("UNSA 2025");
  
  // Conectar a WiFi
  Serial.println();
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);
  Serial.println("Asegúrate de estar en la MISMA RED que el Fog Node");
  Serial.println("(Red WiFi 2.4GHz)");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    WiFi.begin(ssid, password);
    delay(1000);
    Serial.print(".");
    attempts++;
    
    // Mostrar estado cada 5 intentos
    if (attempts % 5 == 0) {
      Serial.println();
      Serial.print("Intento ");
      Serial.print(attempts);
      Serial.print("/30 - Status: ");
      Serial.println(WiFi.status());
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✓ WiFi conectado!");
    Serial.print("   IP Arduino: ");
    Serial.println(WiFi.localIP());
    Serial.print("   RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    
    // Mostrar WiFi conectado en pantalla
    carrier.display.fillScreen(0x07E0);  // Verde
    carrier.display.setTextColor(0x0000);
    carrier.display.setCursor(40, 110);
    carrier.display.print("WiFi OK!");
    delay(1500);
  } else {
    Serial.println();
    Serial.println("✗ Error al conectar WiFi");
    Serial.println("  Verifica SSID y contraseña");
    
    // Mostrar error en pantalla
    carrier.display.fillScreen(0xF800);  // Rojo
    carrier.display.setTextColor(0xFFFF);
    carrier.display.setCursor(20, 110);
    carrier.display.print("WiFi Error!");
    while (1);  // Detener ejecución
  }
  
  // Conectar a MQTT Broker (Fog Node)
  Serial.println();
  Serial.print("Conectando a Fog Node MQTT: ");
  Serial.print(mqtt_broker);
  Serial.print(":");
  Serial.println(mqtt_port);
  
  mqttClient.setId(mqtt_client_id);
  
  if (!mqttClient.connect(mqtt_broker, mqtt_port)) {
    Serial.print("✗ Error de conexión MQTT. Código: ");
    Serial.println(mqttClient.connectError());
    Serial.println("  Verifica:");
    Serial.println("  - IP del Fog Node en mqtt_broker");
    Serial.println("  - Mosquitto está corriendo en Laptop B");
    Serial.println("  - Ambos están en la misma red WiFi");
    
    carrier.display.fillScreen(0xF800);  // Rojo
    carrier.display.setTextColor(0xFFFF);
    carrier.display.setCursor(20, 110);
    carrier.display.print("MQTT Error!");
    while (1);  // Detener ejecución
  }
  
  Serial.println("✓ Conectado al Fog Node!");
  Serial.print("   Topic sensores: ");
  Serial.println(mqtt_topic_sensores);
  Serial.print("   Device ID: ");
  Serial.println(device_id);
  
  // Suscribirse al topic de comandos (para recibir órdenes del Fog)
  mqttClient.subscribe(mqtt_topic_comandos);
  Serial.print("✓ Suscrito a comandos: ");
  Serial.println(mqtt_topic_comandos);
  
  // Publicar mensaje de inicio
  mqttClient.beginMessage(mqtt_topic_status);
  mqttClient.print("Arduino sensor-zona1 conectado al Fog Node");
  mqttClient.endMessage();
  
  // Mostrar MQTT conectado en pantalla
  carrier.display.fillScreen(0x001F);  // Azul
  carrier.display.setTextColor(0xFFFF);
  carrier.display.setCursor(20, 100);
  carrier.display.print("Fog Node OK!");
  carrier.display.setCursor(10, 130);
  carrier.display.setTextSize(1);
  carrier.display.print("Enviando datos...");
  delay(2000);
  
  Serial.println();
  Serial.println("✓ Sistema listo!");
  Serial.println("   Enviando datos cada 5 segundos al Fog Node...");
  Serial.println();
}

// ============================================================================
// LOOP PRINCIPAL
// ============================================================================
void loop() {
  // Mantener conexión MQTT
  mqttClient.poll();
  
  // Verificar si hay mensajes de comandos del Fog
  int messageSize = mqttClient.parseMessage();
  if (messageSize) {
    String topic = mqttClient.messageTopic();
    String message = "";
    
    while (mqttClient.available()) {
      message += (char)mqttClient.read();
    }
    
    Serial.print("📩 Comando del Fog: ");
    Serial.println(message);
    
    // Procesar comando (puedes agregar más comandos aquí)
    if (message == "RESET") {
      Serial.println("   Reiniciando Arduino...");
      delay(1000);
      // Reset via watchdog o manual
    }
  }
  
  // Verificar si es momento de enviar datos
  if (millis() - lastSendTime >= sendInterval) {
    lastSendTime = millis();
    
    // Leer sensores
    float temperatura = carrier.Env.readTemperature();
    float humedad = carrier.Env.readHumidity();
    float presion = carrier.Pressure.readPressure();
    
    // Leer luz (APDS9960)
    int r, g, b;
    while (!carrier.Light.colorAvailable()) {
      delay(5);
    }
    carrier.Light.readColor(r, g, b);
    
    // Calcular luz promedio (aproximación a lux)
    float luz = (r + g + b) / 3.0;
    
    // Mostrar en Serial Monitor
    Serial.println("─────────────────────────────────");
    Serial.print("🌡️  Temperatura: ");
    Serial.print(temperatura, 1);
    Serial.println(" °C");
    
    Serial.print("💧 Humedad: ");
    Serial.print(humedad, 1);
    Serial.println(" %");
    
    Serial.print("🌀 Presión: ");
    Serial.print(presion, 2);
    Serial.println(" kPa");
    
    Serial.print("💡 Luz: ");
    Serial.print(luz, 0);
    Serial.println(" (RGB avg)");
    
    // Mostrar en pantalla del Carrier
    carrier.display.fillScreen(0x0000);
    carrier.display.setTextColor(0xFFFF);
    carrier.display.setTextSize(2);
    
    carrier.display.setCursor(10, 40);
    carrier.display.print("T:");
    carrier.display.print(temperatura, 1);
    carrier.display.print("C");
    
    carrier.display.setCursor(10, 70);
    carrier.display.print("Luz:");
    carrier.display.print(luz, 0);
    
    carrier.display.setCursor(10, 100);
    carrier.display.print("Hum:");
    carrier.display.print(humedad, 1);
    carrier.display.print("%");
    
    carrier.display.setCursor(10, 130);
    carrier.display.setTextSize(1);
    carrier.display.print("Zona1-Arduino");
    
    // Enviar datos vía MQTT al Fog Node
    enviarDatosMQTT(temperatura, luz, humedad, presion);
    
    Serial.println();
  }
  
  delay(100);  // Pequeña pausa
}

// ============================================================================
// FUNCIÓN: Enviar datos vía MQTT al Fog Node
// ============================================================================
void enviarDatosMQTT(float temp, float luz, float hum, float pres) {
  // Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi desconectado. Intentando reconectar...");
    WiFi.begin(ssid, password);
    delay(2000);
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("✗ No se pudo reconectar al WiFi");
      return;
    }
  }
  
  // Verificar conexión MQTT
  if (!mqttClient.connected()) {
    Serial.println("✗ MQTT desconectado. Intentando reconectar...");
    
    if (!mqttClient.connect(mqtt_broker, mqtt_port)) {
      Serial.print("✗ Error de reconexión MQTT. Código: ");
      Serial.println(mqttClient.connectError());
      return;
    }
    
    // Re-suscribirse a comandos
    mqttClient.subscribe(mqtt_topic_comandos);
    Serial.println("✓ Reconectado al Fog Node");
  }
  
  // Crear JSON con los datos (compatible con Fog Processor)
  StaticJsonDocument<256> doc;
  doc["device_id"] = device_id;          // "sensor-zona1"
  doc["temperatura"] = temp;
  doc["luz"] = luz;
  doc["humedad"] = hum;
  doc["presion"] = pres;
  doc["timestamp"] = millis();           // Timestamp local
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.print("📡 Enviando al Fog... ");
  
  // Publicar en MQTT
  mqttClient.beginMessage(mqtt_topic_sensores);
  mqttClient.print(jsonString);
  int result = mqttClient.endMessage();
  
  if (result) {
    Serial.println("✓ Enviado");
    
    // Indicador visual de envío exitoso
    carrier.display.fillRect(200, 10, 30, 30, 0x07E0);  // Verde
  } else {
    Serial.println("✗ Error al enviar");
    
    // Indicador visual de error
    carrier.display.fillRect(200, 10, 30, 30, 0xF800);  // Rojo
  }
}
