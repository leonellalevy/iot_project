from dash import Dash, html, Input, Output, callback
import dash_daq as daq
from LED import LED

# Light images
img_light_off = 'assets/images/lightbulboff.png'
img_light_on = 'assets/images/lightbulbon.png'

# LED INFORMATION
LED_PIN = 27
led = LED(LED_PIN, False)

app = Dash(__name__)

# Phase 1 content
light_content = [
    html.Div(className="card", children=[
        html.H2('LED'),
        html.Img(src=img_light_off, id='light-img', className="feature-img"),
        html.Br(),
        daq.BooleanSwitch(on=False, id='light-switch', className='dark-theme-control'),
    ])
]

# App layout
app.layout = html.Div(id='layout', children=[
    html.H1('IoT Project', style={'margin-top': '20px'}),
    html.Div(id='container', children=[
        html.Div(id='column', children=[
            html.Div(id="right-container", children=[
                html.Div(id='light-container', children=light_content),
            ])
        ])
    ]),
])

# Callback to update the LED state
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
