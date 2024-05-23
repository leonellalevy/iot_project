#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// Network settings
const char* ssid = "Momo";
const char* password = "12345678";
const char* mqtt_server = "172.20.10.9";

// MQTT Client
WiFiClient espClient;
PubSubClient client(espClient);

// GPIO Pin Definitions
const int ledPin = 5; 
const int sensorPin = A0;  

// RFID Settings
#define SS_PIN 15
#define RST_PIN 16
MFRC522 rfid(SS_PIN, RST_PIN); 
MFRC522::MIFARE_Key key;

// Sensor Settings
int sensorValue;
const int threshold = 50;

// MQTT Topics
const char* sensorTopic = "sensor/value";
const char* lightTopic = "room/light";
const char* rfidTopic = "rfid/tag";

void setup() {
  Serial.begin(115200);
  delay(10);

  // Initialize WiFi
  setup_wifi();
  
  // Initialize MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Initialize GPIO
  pinMode(ledPin, OUTPUT);
  pinMode(sensorPin, INPUT);

  // Initialize SPI and RFID
  SPI.begin(); // Ensure SPI doesn't interfere with WiFi setup
  rfid.PCD_Init(); // Init MFRC522

  // Prepare the key (common MIFARE key)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println(message);

  int lightValue = message.toInt();
  Serial.print("Light Value: ");
  Serial.println(lightValue);

  // Check if the light value is below the threshold to turn on the LED
  digitalWrite(ledPin, lightValue < threshold ? HIGH : LOW);
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
  client.publish(sensorTopic, String(sensorValue).c_str());

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    Serial.print("New RFID Tag ID: ");
    String rfidTagID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTagID += String(rfid.uid.uidByte[i], HEX);
    }
    rfidTagID.trim(); // Remove any leading/trailing whitespace
    Serial.println(rfidTagID);
    client.publish(rfidTopic, rfidTagID.c_str());

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  delay(5000); // Manage the delay as necessary
}
