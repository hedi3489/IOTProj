#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "24MHD";
const char* password = "badonkadonka";
const char* mqtt_server = "172.20.10.3";  // MQTT Broker IP address

WiFiClient espClient;
PubSubClient client(espClient);

#define LIGHT_SENSOR_PIN 34
#define SS_PIN 5  // SDA Pin on RC522
#define RST_PIN 4 // RST Pin on RC522
MFRC522 rfid(SS_PIN, RST_PIN); // Create MFRC522 instance

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retryCount++;
    if (retryCount > 30) {  // 15 seconds timeout
      Serial.println("Failed to connect to WiFi.");
      break;
    }
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected. IP address: ");
    Serial.println(WiFi.localIP());
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32LightSensor")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void sendRFIDData() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Prepare the UID message
  char uidMessage[100];
  snprintf(uidMessage, sizeof(uidMessage), "{\"uid\":\"");
  for (byte i = 0; i < rfid.uid.size; i++) {
      char hexBuffer[4];
      snprintf(hexBuffer, sizeof(hexBuffer), "%02X", rfid.uid.uidByte[i]);
      strcat(uidMessage, hexBuffer);
      if (i < rfid.uid.size - 1) {
          strcat(uidMessage, ":");
      }
  }
  strcat(uidMessage, "\"}");

  client.publish("home/rfid", uidMessage);

  // Halt PICC
  rfid.PICC_HaltA();
}

void setup() {
  Serial.begin(115200);
  pinMode(LIGHT_SENSOR_PIN, INPUT);  // Ensure pin is set to input mode
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  // Initialize SPI and RFID
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("Place your RFID card near the reader...");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Handle light sensor readings
  int brightness = 0;
  for (int i = 0; i < 10; i++) {
    brightness += analogRead(LIGHT_SENSOR_PIN);
    delay(10);
  }
  brightness /= 10;

  Serial.print("Brightness: ");
  Serial.println(brightness);

  char msg[50];
  snprintf(msg, sizeof(msg), "%d", brightness);
  client.publish("home/brightness", msg);

  // Handle RFID readings
  sendRFIDData();

  delay(1000);  // Delay to prevent flooding
}