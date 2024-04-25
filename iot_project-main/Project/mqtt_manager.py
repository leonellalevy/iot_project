import threading
import paho.mqtt.client as mqtt
import time

class MQTTManager:
    def __init__(self, broker, port, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.light_intensity = 0
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code: " + str(rc))
        client.subscribe(self.topic)
        self.connected_event.set()

    def on_message(self, client, userdata, msg):
        print("Message received: " + msg.payload.decode())
        try:
            self.light_intensity = float(msg.payload.decode())
            #self.message_received_event.set() 
        except ValueError:
            print("Invalid light intensity value")

    def get_light_intensity(self):
        print(self.light_intensity)
        return self.light_intensity