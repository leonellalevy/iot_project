#imports phase 1
import datetime
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

#import phase 3
from mqtt_manager import MQTTManager
from dash import callback_context

# Light images
img_light_off = 'assets/images/lightbulboff.png'
img_light_on = 'assets/images/lightbulbon.png'

# Fan images
img_fan_on = 'assets/images/fan_on.gif'
img_fan_off = 'assets/images/fan_off.png'

# LED INFORMATION
LED_PIN = 27
led = LED(LED_PIN, False)

#MOTOR INFORMATION
motorE = 16 
motorA = 20
motorB = 21
motor_state = False
motor = DCMotor(motorE,motorA,motorB,motor_state)

#DHT11 INFORMATION
DHT_PIN = 17 
dht = DHT.DHT(DHT_PIN) 

#Decalre mqtt
mqtt_broker = "172.20.10.2"
mqtt_port = 1883
mqtt_topic = "sensor/value"

global mqtt_manager
mqtt_manager = None

def setup_mqtt():
    global mqtt_manager
    mqtt_manager = MQTTManager(mqtt_broker, mqtt_port, mqtt_topic)

setup_mqtt() 

#CONSTANTS
threshold = 24
threshold_brightness = 600

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
sensor_value_display = [
    html.Div(className="card", children=[
        html.H2('Sensor Value'),
        daq.Gauge(
            id='sensor-value-gauge',
            color={"gradient":True,"ranges":{"green":[0,100],"yellow":[100,200],"red":[200,300]}},
            showCurrentValue=True, 
            max=1000,
            min=0,
            value=0
        ),
    ])
]

# App layout
app.layout = html.Div(id='layout', children=[
    html.H1('IoT Project', style={'margin-top': '20px'}),
    html.Div(id='container', children=[
        html.Div(id='column', children=[
            html.Div(id="right-container", children=[
                html.Div(id='light-container', children=light_display),
                html.Div(id='sensor-container', children=temp_humidity_display),
                html.Div(id='sensor-value-container', children=sensor_value_display)
            ])
        ])
    ]),
    dcc.Interval(id='email-interval', interval=5*1000, n_intervals=0),
    dcc.Interval(id='refresh', interval=2*1000, n_intervals=0)
])

# Callback LED state
@app.callback(
    Output('light-img', 'src'),
    [Input('light-switch', 'on'),
     Input('email-interval', 'n_intervals')]
)
def update_led_combined(on, n_intervals):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'light-switch':
        if on:
            led.turn_on()
            return img_light_on
        else:
            led.turn_off()
            return img_light_off
        #send email for light
    elif triggered_id == 'email-interval':
        light_intensity = mqtt_manager.get_light_intensity()
        if light_intensity < threshold_brightness:
            current_time = datetime.datetime.now().strftime("%H:%M")
            subject = "Light Notification"
            body = f"The light is ON at {current_time}."
            email_manager.send_email(subject, body)
            print('Email sent for light')
            return img_light_on
        else:
            return img_light_off
    else:
        return img_light_off

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


    if temp > threshold:
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

@app.callback(
    Output('sensor-value-gauge', 'value'),
    Input('refresh', 'n_intervals')
)
def update_sensor_value(n_intervals):
    global mqtt_manager
    if mqtt_manager is not None:
        return mqtt_manager.get_light_intensity()
    return 0 

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
