#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Uzi";
const char* password = "uzikanoozi";
const char* mqtt_server = "172.20.10.2";  // MQTT Broker IP address

WiFiClient espClient;
PubSubClient client(espClient);

#define LIGHT_SENSOR_PIN 34

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
    if (retryCount > 30) {  // 15 seconds timeout (if still not connected, stop trying)
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

void setup() {
  Serial.begin(115200);
  pinMode(LIGHT_SENSOR_PIN, INPUT);  // Ensure pin is set to input mode
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int brightness = 0;
  for (int i = 0; i < 10; i++) {
    brightness += analogRead(LIGHT_SENSOR_PIN);
    delay(10);
  }
  brightness /= 10;
  
  Serial.print("Brightness: ");
  Serial.println(brightness);
  delay(1000);  // 1-second delay

  char msg[50];
  snprintf(msg, sizeof(msg), "%d", brightness);
  client.publish("home/brightness", msg);

  //delay(1000);
}