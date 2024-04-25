import paho.mqtt.client as mqtt
import time

class MQTTManager:
    def __init__(self, broker, port, topic):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.broker = broker
        self.port = port
        self.topic = topic
        self.light_intensity = 0
        
        # Set the connection and message callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect and start the loop after setting the callbacks
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code: " + str(rc))
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print("Message received: " + msg.payload.decode())
        try:
            self.light_intensity = int(msg.payload.decode())
        except ValueError:
            print("Invalid light intensity value")

    def get_light_intensity(self):
        print(self.light_intensity)
        return self.light_intensity
