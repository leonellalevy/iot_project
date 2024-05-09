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
from motor import Motor
from email_manager import EmailManager

#import phase 3
from mqtt_manager import MQTTManager
from dash import callback_context

#import phase 4
from user import User

# Light and Fan images
img_light_off = 'assets/images/lightbulboff.png'
img_light_on = 'assets/images/lightbulbon.png'
img_fan_on = 'assets/images/fan_on.gif'
img_fan_off = 'assets/images/fan_off.png'

# GPIO pins
LED_PIN = 27
MOTOR_E = 16
MOTOR_A = 20
MOTOR_B = 21
DHT_PIN = 17

motor_state=False
#Initialize components
led = LED(LED_PIN, False)
motor = Motor(MOTOR_E, MOTOR_A, MOTOR_B, motor_state)
dht = DHT.DHT(DHT_PIN) 
#led = None
#motor = None
#dht = None

# Email credentials and recipients
sender = "arianelevymartel@gmail.com"
password = "jwzdcnmbmzypdjeh"
recipients = "sachabloup@gmail.com"

# CONSTANTS
token_length = 10
email_count = 0
subject = ""
body = ""

# Email, database and MQTT setup
email_count = 0
#mqtt_broker =  "192.168.56.1"
mqtt_broker = "172.20.10.9"
#mqtt_broker = "192.168.0.107"
mqtt_port = 1883
mqtt_topic = ["sensor/value","rfid/tag"]
mqtt_manager = None
current_user = None
db_file = "/home/olabodejire/Documents/iot_project-main/iot_project-main/Project/assets/Database/bob.db"

def setup_mqtt():
    global mqtt_manager
    mqtt_manager = MQTTManager(mqtt_broker, mqtt_port, mqtt_topic, db_file)
    mqtt_manager.set_user_callback(handle_user_update)

def setup_email():
    global email_manager_fan, email_manager_led, email_manager_user
    email_manager_fan = EmailManager(sender, password, recipients)
    email_manager_led = EmailManager(sender, password, recipients)
    email_manager_user = EmailManager(sender, password, recipients)

def handle_user_update(user_info):
    global current_user
    current_user = user_info

    if current_user:
        current_time = datetime.datetime.now().strftime("%H:%M")
        subject = "User Entry Notification"
        body = f"User {current_user.name} entered at {current_time}."
        email_manager_user.send_email(subject, body)
        print('Email sent for user entry')

        # Print user information to the terminal
        print(f"User Info: RFID - {current_user.rfid}, Name - {current_user.name}, "
              f"Temperature Threshold - {current_user.temp_threshold}, Light Threshold - {current_user.light_threshold}")

#Setting up everything
setup_mqtt()
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

#Contenu de phase 4
user_info_display = [
    html.Div(className="card", children=[  # Removed the ID here if not needed elsewhere
        html.H2('User Information'),
        html.Div(id='user-info', children=[
            html.P("RFID:"),
            html.P("Name:"),
            html.P("Temperature Threshold:"),
            html.P("Light Threshold:"),
        ]),
    ])
]

#-------------Display of the application-----------
app.layout = html.Div(id='layout', children=[
    html.H1('IoT Project', style={'margin-top': '20px'}),
    html.Div(id='container', children=[
        html.Div(id='column', children=[
            html.Div(id="right-container", children=[
                html.Div(id='light-container', children=light_display),
                html.Div(id='sensor-container', children=temp_humidity_display),
                html.Div(id='sensor-value-container', children=sensor_value_display),
                html.Div(id='user-info-container', children=user_info_display)  # This ID is now unique
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
    elif triggered_id == 'email-interval':
        if current_user is not None:
            light_intensity = mqtt_manager.get_light_intensity()
            if light_intensity < current_user.light_threshold:
                current_time = datetime.datetime.now().strftime("%H:%M")
                subject = "Light Notification"
                body = f"The light is ON at {current_time}."
                email_manager_led.send_email(subject, body)
                print('Email sent for light')
                return img_light_on
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
    global fan_state, email_count, token
    print("test 1")
    # Check if current_user is None
    if current_user is None:
        print("test 2")
        print("No current user set")
        return img_fan_off  # Return default image if no user is set

    # Proceed if current_user is not None
    if temp > current_user.temp_threshold:
        print("test 3")
        if not fan_state:
            if email_count == 0:
                email_count = 1
                token = email_manager_fan.generate_token(token_length)
                print(f"Token: {token}")
                subject = f'{token}'
                body = f'Hello! This message is to let you know that the current temperature is {temp}°C. ' \
                       f'Do you want to turn it on? If the answer is yes, please answer the email with the word <Yes>. ' \
                       f'Have a nice day!'
                email_manager_fan.send_email(subject, body)
                print('Email sent for fan')

            client_reply = email_manager_fan.read_email(token, temp)
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

@app.callback(
    Output('user-info', 'children'),
    Input('refresh', 'n_intervals')
)
def update_user_info(n_intervals):
    if current_user:
        return [
            html.P(f"RFID: {current_user.rfid}"),
            html.P(f"Name: {current_user.name}"),
            html.P(f"Temperature Threshold: {current_user.temp_threshold}"),
            html.P(f"Light Threshold: {current_user.light_threshold}"),
        ]
    else:
        return [
            html.P("RFID:"),
            html.P("Name:"),
            html.P("Temperature Threshold:"),
            html.P("Light Threshold:"),
        ]
    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
