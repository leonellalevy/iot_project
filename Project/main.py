# Import packages
from dash import Dash, html, Input, Output, State, callback, dcc
import dash_daq as daq
import time
from time import sleep
from LED import LED

# Light images
img_light_off = 'assets/images/light_off.png'
img_light_on = 'assets/images/light_on.png'

# LED INFORMATION
LED_PIN = 16
led = LED(LED_PIN,False)

app = Dash(__name__)

# Phase 1 content
light_content =[
        
    html.Div(className="card-component", children=[

        html.H3('LED'),
        html.Div([
            html.Img( src=img_light_off, id='light-img', className="feature-img" )
        ]),
        html.Br(),
        daq.BooleanSwitch( on=False, id='light-switch', className='dark-theme-control' ),
    ])
        
]

# App layout
app.layout = html.Div( id='layout',
    children=[
        
        html.H1(style={},children=['IoT Project']),
        html.Div(id='container', children=[
            
            html.Div(id='column', children=[

                html.Div(id="right-container", children=[
                    html.Div(id='light-container', children=light_content),
                ])

            ])
        ]),

    ]
)

# Run the app
if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    app.run(debug=True)
    