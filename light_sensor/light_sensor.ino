#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Uzi";
const char* password = "uzikanoozi";

const char* mqtt_server = "172.20.10.6";  // Your MQTT Broker IP address (Windows machine)
WiFiClient espClient;
PubSubClient client(espClient);

#define LIGHT_SENSOR_PIN 34  // Pin where the light sensor is connected (change this to your actual pin)

long lastMsg = 0;
char msg[50];

#define ANALOG_THRESHOLD  400  // Adjust this threshold as needed

void setup() {
  Serial.begin(115200);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  
  // Set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("mqtt-explorer-118b8b78")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);  // Retry after 5 seconds
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  int analogValue = analogRead(LIGHT_SENSOR_PIN);
  Serial.print("Light sensor value: ");
  Serial.println(analogValue);

  char msg[50];
  snprintf(msg, 50, "Light sensor value: %d", analogValue);
  
  if (millis() - lastMsg > 5000) {
    client.publish("sensor/light_value", msg);  // Publish to the "sensor/light_value" topic
    lastMsg = millis();
  }

  client.loop();
}
