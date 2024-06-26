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
import bluetooth

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
fan_state = False
led_state = False
#Initialize components
led = LED(LED_PIN, False)
motor = Motor(MOTOR_E, MOTOR_A, MOTOR_B, motor_state)
dht = DHT.DHT(DHT_PIN) 
motor.setupMotorState(fan_state)
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

bluetooth_devices = set()

# Modify scan_bluetooth to return the list of Bluetooth addresses
def scan_bluetooth(threshold_rssi):
    global bluetooth_devices
    nearby_devices = bluetooth.discover_devices(duration=8)  # Discover nearby devices
    new_devices = set()
    for addr in nearby_devices:
        new_devices.add(addr)
    added_devices = new_devices - bluetooth_devices  # New devices compared to previous scan
    bluetooth_devices = new_devices  # Update the global variable with the new list
    return list(added_devices) 

#---------------------START OF THE APPLICATION-----------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1('LOM Home', style={'textAlign': 'center'}),
    html.Div(className="container", children=[
        html.Div(className="user-info", id="user-info", children=[
            html.H3('User Information'),
            html.P("RFID:"),
            html.P("Name:"),
            html.P("Temperature Threshold:"),
            html.P("Light Threshold:"),
        ]),
        html.Div(className="right-content", children=[
            html.Div(className="row", children=[
                html.Div(className="column", children=[
                    html.H3('Temperature (°C)'),
                    daq.Thermometer(id='temp_thermometer', value=0, min=10, max=40, height=150, showCurrentValue=True)
                ]),
                html.Div(className="column", children=[
                    html.H3('Humidity (%)'),
                    daq.Gauge(id='humidity-gauge', value=50, min=0, max=100, showCurrentValue=True)
                ]),
                html.Div(className="column", children=[
                    html.H3('Sensor Value'),
                    daq.Gauge(id='sensor-value-gauge', value=0, min=0, max=1000, showCurrentValue=True)
                ]),
            ]),
            html.Div(className="row", children=[
                html.Div(className="column", children=[
                    html.H3('LED Control'),
                    html.Img(src=img_light_off, id='light-img', style={'width': '100px'}),
                    daq.BooleanSwitch(id='light-switch', on=False)
                ]),
                html.Div(className="column", children=[
                    html.H3('Fan Status'),
                    html.Img(src=img_fan_off, id='fan-img', style={'width': '100px'}),
                ]),
                html.Div(className="column", children=[
                html.H3('Bluetooth Devices'),
                daq.LEDDisplay(id='bluetooth-count', value="0", color="#92e0d3", backgroundColor="#1e2130"),
                daq.BooleanSwitch(id='bluetooth-scan-switch', on=False),
                dcc.Interval(id='bluetooth-scan-interval', interval=3000, n_intervals=0, disabled=True)
                ])
            ])
        ])
    ]),
    dcc.Interval(id='email-interval', interval=5*1000, n_intervals=0),
    dcc.Interval(id='refresh', interval=2*1000, n_intervals=0)
])

# Callback LED state
@app.callback(
    [Output('light-img', 'src'), Output('light-switch', 'on')],
    [Input('light-switch', 'on'),
     Input('email-interval', 'n_intervals')]
)
def update_led_combined(on, n_intervals):
    global led_state
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'light-switch':
        led_state = True
        if on:
            led.turn_on()
            return img_light_on, True
        else:
            led.turn_off()
            return img_light_off, False
    elif triggered_id == 'email-interval':
        if current_user is not None:
            light_intensity = mqtt_manager.get_light_intensity()
            if light_intensity < current_user.light_threshold:
                led_state = True
                led.turn_on()
                current_time = datetime.datetime.now().strftime("%H:%M")
                subject = "Light Notification"
                body = f"The light is ON at {current_time}."
                email_manager_led.send_email(subject, body)
                print('Email sent for light')
                return img_light_on, True    
        led_state = False
        led.turn_off()
        return img_light_off, False
    else:
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
    

@app.callback(
    Output('bluetooth-count', 'value'),
    Output('bluetooth-count', 'color'),
    Input('bluetooth-scan-switch', 'on'),
    Input('bluetooth-scan-interval', 'n_intervals'),
)
def update_bluetooth_count_and_track_devices(on, n_intervals):
    global bluetooth_devices
    if on:
        new_devices = scan_bluetooth(-50)
        bluetooth_count = len(bluetooth_devices)
        color = "#92e0d3"  
        if new_devices:
            color = "#FF0000" 
            print(f"New Bluetooth Devices: {new_devices}")
        return str(bluetooth_count), color
    return "0", "#92e0d3" 

if __name__ == '__main__':
    app.run_server(debug=True)
