#imports phase 1
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

# Light images
img_light_off = 'assets/images/lightbulboff.png'
img_light_on = 'assets/images/lightbulbon.png'

# Fan images
fan_on = 'assets/images/fan_on.gif'
fan_off = 'assets/images/fan_off.png'

# LED INFORMATION
LED_PIN = 27
led = LED(LED_PIN, False)

#MOTOR INFORMATION
motorE = 22 
motorA = 27
motorB = 18
motor_state = False
motor = DCMotor(motorE,motorA,motorB,motor_state)

#DHT11 INFORMATION
DHT_PIN = 26 
dht = DHT.DHT(DHT_PIN) 

#CONSTANTS
threshold = 24
token_length = 16
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
                html.Img(src='assets/images/fan_off.png', id='fan-img', className="feature-img" ),
            ]),
        ])
]

# App layout
app.layout = html.Div(id='layout', children=[
    html.H1('IoT Project', style={'margin-top': '20px'}),
    html.Div(id='container', children=[
        html.Div(id='column', children=[
            html.Div(id="right-container", children=[
                html.Div(id='light-container', children=light_display),
                html.Div(id='sensor-container', children=temp_humidity_display)
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
    

def getDHT11Info():
    for i in range(0,15):
        chk = dht.readDHT11()	
        if(chk is dht.DHTLIB_OK):	
            break

    data=[]
    data.append(dht.temperature)
    data.append(dht.humidity)
    return data

# Callback temperature and humidity values
@app.callback(
    Output('temp_thermometer', 'value'),
    Output('humidity-gauge', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_thermometer_gauge(n):
    DHT11_data = dht.getDHT11Info()
    temp = DHT11_data[0]
    humid = DHT11_data[1]
    return temp,humid

# Callback for updating the fan image based on temperature
@app.callback(
    Output('fan-img', 'src'),
    Input('temp_thermometer', 'value'),  # Use temperature value as input
    Input('email-interval', 'n_intervals'),
)
def update_fan(temp, n_intervals):
    global fan_state
    global email_count
    global unique_token

    print('Temperature:', temp)
    
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
                motor.setupMotorState(fan_state)
                return fan_on, 'Fan is ON'
            else:
                fan_state = False
                motor.setupMotorState(fan_state)
                return fan_off, 'Fan is OFF'
        else:
            return fan_on, 'Fan is ON'
    else:
        email_count = 0
        fan_state = False
        motor.setupMotorState(fan_state)
        return fan_off, 'Fan is OFF'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
