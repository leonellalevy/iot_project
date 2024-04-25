#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Network settings
const char* ssid = "Leo";
const char* password = "Michi1739$";
const char* mqtt_server = "172.20.10.2";

// MQTT Client
WiFiClient espClient;
PubSubClient client(espClient);

// GPIO Pin Definitions
const int ledPin = 5; 
const int sensorPin = A0; 

// Sensor Settings
int sensorValue;
const int threshold = 500;

// MQTT Topics
const char* sensorTopic = "sensor/value";
const char* lightTopic = "room/light";

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(ledPin, OUTPUT);
  pinMode(sensorPin, INPUT);
}

void setup_wifi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");

  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  if (strcmp(topic, lightTopic) == 0) {
    
    Serial.print("LED control message, sensor value: ");
    Serial.println(message);

    // Control the LED based on the value
    if (message.toInt() < threshold) {
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
    }
  } else if (strcmp(topic, sensorTopic) == 0) {
    // This prints the sensor value directly if subscribed to the sensor value topic
    Serial.print("Sensor reading: ");
    Serial.println(message);
  }
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      client.subscribe(lightTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  sensorValue = analogRead(sensorPin);
  Serial.print("Current Sensor Value: ");
  Serial.println(sensorValue);

  String sensorStr = String(sensorValue);
  client.publish(sensorTopic, sensorStr.c_str());

  
  client.publish(lightTopic, sensorStr.c_str());

  delay(1000);
}
