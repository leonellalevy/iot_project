class User:
    def __init__(self, rfid, name, temp_threshold, light_threshold):
        self.rfid = rfid
        self.name = name
        self.temp_threshold = temp_threshold
        self.light_threshold = light_threshold

