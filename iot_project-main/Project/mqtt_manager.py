import paho.mqtt.client as mqtt
import time
from db import DBManager
from user import User

class MQTTManager:
    def __init__(self, broker, port, topic, db_file):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.broker = broker
        self.port = port
        self.topic = topic
        self.light_intensity = 0
        self.db_manager = DBManager(db_file)
        self.user = None
        self.user_callback = None
        
        # Set the connection and message callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect and start the loop after setting the callbacks
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code: " + str(rc))
        client.subscribe(self.topic[0])
        client.subscribe(self.topic[1])

    def on_message(self, client, userdata, msg):
        print("Message received on topic {}: {}".format(msg.topic, msg.payload.decode()))
        if msg.topic == self.topic[0]:
            try:
                self.light_intensity = int(msg.payload.decode())
            except ValueError:
                print("Invalid light intensity value")
        elif msg.topic == self.topic[1]:
            try:
                rfid = str(msg.payload.decode())
                userExist = self.db_manager.check_user_exists(rfid)

                if userExist:
                    user_info = self.db_manager.get_user_thresholds(rfid)
                    self.user = User(rfid, user_info[1], user_info[2], user_info[3])

                    if self.user_callback:
                        self.user_callback(self.user)
                    print("User information updated!")
                else:
                    print("The user does not exist in the database")
            except ValueError:
                print("Invalid user information value")
        else:
            print("Received message on an unexpected topic:", msg.topic)

    def get_light_intensity(self):
        return self.light_intensity
    
    def set_user_callback(self, callback):
        self.user_callback = callback
    
