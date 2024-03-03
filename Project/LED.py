import RPi.GPIO as GPIO

class LED:
    pin = 27
    state = False
    
    def __init__(self, pin, initial_state):
        self.state = initial_state

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin,GPIO.OUT,initial=state)

    def turn_on(self):
        self.state = True

    def turn_off(self):
        self.state = False

    def setupLEDState(self,state):
        if(state == True):
            GPIO.output(self.pin,1)
        else:
            GPIO.output(self.pin,0)