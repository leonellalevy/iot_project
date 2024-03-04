import RPi.GPIO as GPIO

class LED:
    def __init__(self, pin, initial_state=False):
        self.pin = pin
        self.state = initial_state

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT, initial=self.state)

    def turn_on(self):
        self.state = True
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        self.state = False
        GPIO.output(self.pin, GPIO.LOW)

    def setupLEDState(self, state):
        if state:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)
