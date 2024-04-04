import RPi.GPIO as GPIO

class DCMotor:    
    def __init__(self,MotorE,MotorA,MotorB,state=False):
        self.MotorE = MotorE
        self.MotorA = MotorA
        self.MotorB = MotorB
        
        self.state = state

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MotorE,GPIO.OUT)
        GPIO.setup(MotorA,GPIO.OUT)
        GPIO.setup(MotorB,GPIO.OUT)

    def setupMotorState(self,state):
        if(state == True):
            GPIO.output(self.MotorE,GPIO.HIGH)
            GPIO.output(self.MotorA,GPIO.LOW)
            GPIO.output(self.MotorB,GPIO.HIGH)
        else:
            GPIO.output(self.MotorE,GPIO.LOW)
            GPIO.output(self.MotorA,GPIO.LOW)
            GPIO.output(self.MotorB,GPIO.LOW)
