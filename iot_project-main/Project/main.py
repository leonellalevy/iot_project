#imports phase 1
from datetime import datetime
from dash import Dash, html, Input, Output, callback, dcc
import dash_daq as daq
from LED import LED

#imports phase 2
import smtplib
import imaplib
import email
import Freenove_DHT as DHT
from DCMotor import DCMotor
from email_manager import EmailManager

#imports phase 3
import paho.mqtt.client as mqtt
from mqtt_manager import MQTTManager

#for Test
import random

# Light images
img_light_off = 'assets/images/lightbulboff.png'
img_light_on = 'assets/images/lightbulbon.png'

# Fan images
img_fan_on = 'assets/images/fan_on.gif'
img_fan_off = 'assets/images/fan_off.png'

# Initialize managers
email_manager = None
mqtt_manager = None

# LED INFORMATION
LED_PIN = 27
led = None
led = LED(LED_PIN, False)

#MOTOR INFORMATION
motorE = 16 
motorA = 20
motorB = 21
motor_state = False
# motor = None # for test
motor = DCMotor(motorE,motorA,motorB,motor_state)

#DHT11 INFORMATION
DHT_PIN = 17 
dht = None
# dht = DHT.DHT(DHT_PIN) 

#CONSTANTS
threshold_temperature = 24
threshold_brightness = 50
token_length = 16
fan_state = False
subject = ""
body = ""
sender = "arianelevymartel@gmail.com"
password = "jwzdcnmbmzypdjeh"
recipients = "sachabloup@gmail.com"

# EMAIL INFORMATION 
email_count = 0
# Function to set up EmailManager
def setup_email():
    global email_manager
    email_manager = EmailManager(sender, password, recipients)

setup_email()

#MQTT INFORMATION
mqtt_broker = "10.0.0.101"
mqtt_port = 1883
mqtt_topic = "sensor/value"

def setup_mqtt():
    global mqtt_manager
    mqtt_manager = MQTTManager(mqtt_broker, mqtt_port, mqtt_topic)
    mqtt_manager.connected_event.wait(timeout=10)

#---------------------START OF THE APPLICATION-----------------------
app = Dash(__name__)

# Contenu de phase 1
light_display = [
    html.Div(className="card", children=[
        html.H2('LED'),
        html.Img(src=img_light_off, id='light-img', className="feature-img"),
        html.Br(),
        daq.BooleanSwitch(on=False, id='light-switch', className='dark-theme-control'),
    ])
]

#Contenu de phase 2
temp_humidity_display = [
    html.Div(className="card", children=[
        html.H2('Temperature (°C)'),
        daq.Thermometer(
            id='temp_thermometer',
            showCurrentValue=True, 
            height=120,
            max=40,
            min=10,
            value=0
        ),
    ]),
    html.Div(className="card", children=[
        html.H2('Humidity (%)'),
        daq.Gauge(
            id='humidity-gauge',
            color={"gradient":True,"ranges":{"green":[0,60],"yellow":[60,80],"red":[80,100]}},
            showCurrentValue=True, 
            max=100,
            min=0,
            value=0
        ),
    ]),
    html.Div(className="card", children=[
        html.H2('Fan'),
        html.Div(children=[
                html.Img(src=img_fan_off, id='fan-img', className="feature-img" ),
            ]),
        ])
]

#Contenu de phase 3
light_intensity_display=[
    html.Div(className="card", children=[
        html.H2('Light Intensity'),
        html.Div([
            html.Div(id='bulb', className='bulb', children=[
                html.Div(id='light', className='light')
                ])
        ]),
        daq.Gauge(
            id='light-intensity-gauge',
            color={"gradient":True,"ranges":{"green":[0,400],"yellow":[400,700],"red":[700,1000]}},
            showCurrentValue=True, 
            max=1000,
            min=0,
            value=0
        ),
    ]),
]

#button = html.Button('Update Bulb', id='update-bulb-button') #for test
# App layout
app.layout = html.Div(id='layout', children=[
    html.H1('IoT Project', style={'margin-top': '20px'}),
    html.Header([
        html.Link(
            rel='stylesheet',
            href='/assets/styles.css' 
        )
    ]),
    html.Div(id='container', children=[
        html.Div(id='column', children=[
            html.Div(id="right-container", children=[
                html.Div(id='light-container', children=light_display),
                html.Div(id='sensor-container', children=temp_humidity_display),
                html.Div(id='photoresistor-container', children=light_intensity_display),
                #button #for test
            ])
        ])
    ]),
    dcc.Interval(id='email-interval', interval=5*1000, n_intervals=0),
    dcc.Interval(id='refresh', interval=2*1000, n_intervals=0)
])

# Callback LED state
@app.callback(
    Output('light-img', 'src'),
    Output('light-switch', 'on'),
    Input('light-switch', 'on'),
)
def update_led(on):
    if on:
        led.turn_on()
        return img_light_on, True
    else:
        led.turn_off()
        return img_light_off, False
    

# Callback temperature and humidity values
@app.callback(
    Output('temp_thermometer', 'value'),
    Output('humidity-gauge', 'value'),
    Input('refresh', 'n_intervals')
)
def update_thermometer_gauge(n_intervals):
    for i in range(0,15):
        chk = dht.readDHT11()	
        if(chk is dht.DHTLIB_OK):	
            break
    temp = dht.temperature
    humid = dht.humidity
    return temp,humid

# Callback for updating the fan image based on temperature
@app.callback(
    Output('fan-img', 'src'),
    Input('temp_thermometer', 'value'),  
    Input('email-interval', 'n_intervals'),
)
def update_fan(temp, n_intervals):
    global fan_state
    global email_count
    global unique_token


    if temp > threshold_temperature:
        if not fan_state:
            if email_count == 0:
                email_count = 1
                unique_token = email_manager.generate_token(token_length)
                subject = f'{unique_token}'
                body = f'The current temperature is {temp}°C. Would you like to turn on the fan?'
                email_manager.send_email(subject, body)
                print('Email sent')

            # Check for client reply
            client_reply = email_manager.read_recent_email_reply(unique_token, temp)
            print('Client reply:', client_reply)

            if client_reply:
                fan_state = True
                print("Fan is on")
                motor.setupMotorState(fan_state)
                return img_fan_on
            else:
                fan_state = False
                motor.setupMotorState(fan_state)
                return img_fan_off
        else:
            return img_fan_on
    else:
        email_count = 0
        fan_state = False
        motor.setupMotorState(fan_state)
        return img_fan_off

# Update the callback to adjust the brightness variable based on the gauge value
@app.callback(
    Output('bulb', 'style'),
    Input('light-intensity-gauge', 'value'),
    #prevent_initial_call=True #for test
)
def update_bulb_style(gauge_value):
    global light_intensity
    light_intensity = mqtt_manager.get_light_intensity()
    brightness = min(light_intensity / 1000.0, 1.0) * 100
    print(brightness)
    #brightness = gauge_value / 10  # Example: Adjust the range if needed
    return {'--brightness': f'{brightness}%'}

# Callback for updating the fan image based on temperature
@app.callback(
    Output('light-img', 'src'),
    Output('light-switch', 'on'),
    Input('light-switch', 'value'),  
    Input('email-interval', 'n_intervals')
)
def update_light_depending_brightness(temp, n_intervals):

    if light_intensity < threshold_brightness:
        current_time = datetime.now().strftime("%H:%M")
        subject = "Light Notification"
        body = f"The light is ON at {current_time} time."
        email_manager.send_email(subject, body)
        print('Email sent')
        led.turn_on()
        return img_light_on, True

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
