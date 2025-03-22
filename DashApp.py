from dash import Dash, html, dcc, Output, Input, State, dash_table
import dash.html as html
import dash_bootstrap_components as dbc
import subprocess
import dash_cytoscape as cyto
import os
import json
import jsonpickle
import plotly.io as pio
import dash
import plotly.graph_objects as go
from countryProportion import generateProportion
from plotGraph import plotCountConnections,plotDistributionSubPlot, plotIndiConnAgeGroup
import shutil
from generateTable import generate_contact_matrix_table,generate_vaccination_impact_contact_patterns_table

current_dir = os.path.dirname(os.path.abspath(__file__))
templatePath = os.path.join(current_dir, "SPAIR.py")
statusPath = os.path.join(current_dir, "./data/status.json")

# Create the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP,dbc.icons.FONT_AWESOME])
server = app.server



dailyNetwork = None  # this hold the recently generated network
infectionGraph = None
populationPie = None
stackBarPlot = None
countPlot = None
distributionSubPlot = None
indiAgeFreqPlot = None
infectionRatePlot = None
degreeVsInfectionPlot = None
truePositiveRatePlot = None
overallInfectionRate = 0  
dayInfectionRateList = []
avgDailyConnectionsList = []
currVer = []
prevVer = []
current_day = 0

app.layout = html.Div([

    # Header section (optional)
    html.Div([
        html.H1("Covid-19 Simulation", style={'text-align': 'center', 'color': '#FFFFFF'}),
    ], style={'background-color': '#007BFF', 'padding': '10px', 'border-radius': '5px'}),

    # Main container with grid layout
    html.Div([
        # Left panel - Input Section
        html.Div([
            # First part: Input section at the top
            html.Div([
                html.H3("Simulation Parameters", style={'text-align': 'center', 'color': '#FFFFFF'}),

                html.P([f"Seed Number",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="A random number, ensuring reproducibility of the same random sequence when used again.")]),
                dcc.Input(id='seed-input', type='number', value=123, className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Reproduction Number",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="The average number of people an infected person will spread a disease to")]),
                dcc.Input(id='reproNum-input', type='number', step=0.1, value=3.5, min = 1.0, max = 20, className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),  

                html.P([f"Population",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Size of population")]),
                dcc.Input(id='population-input', type='number', value=100, min = 20, max=200, placeholder='Enter population', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Days",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Number of simulation days")]),
                dcc.Input(id='day-input', type='number', value=100, min = 1, placeholder='Enter days', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),
                
                html.P([f"Infected population",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Probability: 85% presymptomatic 15% asymptomatic")]),
                html.Div([
                dcc.Input(id='affected-input', type='number', value=5, min = 0, placeholder='Enter number of affected', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Intervention Day",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="The day vaccination is implemented to population (Not on Day 1)")]),
                dcc.Input(id='interventionDay-input', type='number', value=34, min = 2, placeholder='Enter Vaccination Intervention Day', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),          

                html.P([f"Vaccination rate",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="The day vaccination is implemented to population (Not on Day 1)")]),
                dcc.Input(id='vacPercent-input', type='number', value=2.5, min = 0, max = 100, placeholder='Enter Percentage', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '160px', 'height': '25px', 'font-size': '15px'}),          
                dbc.Button(
                    'Generate',
                    id='generate-button',
                    n_clicks=0,
                    style={
                        'margin-left': '10px',
                        'margin-bottom': '3px',
                        'font-size': '15px',  # Keep your font size
                        'height': '27px',
                        'width': '100px',
                        'padding':'3px 10px'
                    },
                    className='btn btn-primary',  # Bootstrap primary button style
                    size='md'                     # Medium size button (optional)
                )],style={'display': 'inline-block'}),
                dcc.ConfirmDialog(
                    id='error-popup',
                    displayed=False  # Initially hidden
                ),
                html.P([f"Age Group Composition Adjustment",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="Country Selection for Age Group Composition Adjustment")]),

                dcc.Dropdown(
                    sorted(['Singapore', 'Japan', 'United States','New Zealand','Australia']),
                    id='dropdown-1',
                    placeholder="Country",
                    searchable=False,optionHeight=20,
                    style={'margin-bottom': '10px', 'font-size': '15px', 'width': '160px'}    # Set the height
                ),
                dcc.Slider(
                    id='slider-2', min=1950, max=2023, step=1, 
                    value=2023, marks={1950: '1950', 2023: '2023'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div([
                    html.Label("Age Group (0 - 9)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-1', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]), 
                
                html.Div([
                    html.Label("Age Group (10 - 19)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-2', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]), 
                
                html.Div([
                    html.Label("Age Group (20 - 29)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-3', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (30 - 39)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-4', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (40 - 49)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-5', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (50 - 59)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-6', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (60 - 69)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-7', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (> 70)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-8', type='number', min=0, step=0.1, value=12.5,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),

                html.P(id='total-output', style={'color': 'red'}),
                dcc.RadioItems(
                    id='connection-radio',
                    options=[
                        {'label': ' Same Daily Network', 'value': 'same'},
                        {'label': ' Dynamic Daily Network', 'value': 'dynamic'},
                        {'label': ' Complete Daily Network', 'value': 'complete'},
                    ],
                    value='same',
                    style={'margin-bottom': '15px', 'color': 'white'}
                ),

                html.Div(id='output-div', style={'margin-top': '15px', 'color': 'white'}),

                html.P("*Only applies when re-generated", style={'margin-bottom': '5px'}),
                dcc.Checklist(id='checkbox-list',
                              options=[{'label': ' Remove Non-Selected Node Connections', 'value': 'removeOthers'},
                                       {'label': ' Isolate Node in Infectious state*', 'value': 'isolate'},
                                       {'label': ' Include Age factor*', 'value': 'age'},
                                       {'label': ' Include Vaccination factor*', 'value': 'vaccination'}],
                              value=[],
                              labelStyle={'margin-right': '10px'},
                              style={'color': 'white', 'margin-bottom': '15px'}),

                dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
                dbc.Progress(id="progress", value=0, label="", color="success",style={'margin-bottom': '15px','--bs-progress-bar-color': 'black','--bs-progress-font-size': '0.9rem'}),
                # Button to trigger modal (popup)
                dbc.Button('Compare Previous', id='open-modal-btn', n_clicks=0,
                            style={
                            'margin-bottom': '5vh',
                            'font-size': '15px',  # Keep your font size
                            'height': '27px',
                            'width': '150px',
                            'padding':'3px 10px'
                            },
                            className='btn btn-primary',  # Bootstrap primary button style
                            size='md'                     # Medium size button (optional)
                ),
                html.P("Notes:",style={'margin-bottom': '1vh'}),
                html.P("Base Reproduction Number: 3.5"),
                html.P("S (Susceptible): People who can catch the disease."),
                html.P("P (Presymptomatic): Infected, not showing symptoms yet, but can spread the disease."),
                html.P("A (Asymptomatic): Infected with no symptoms, but can still spread the disease."),
                html.P("I (Infectious): Infected, showing symptoms, can spread the disease."),
                html.P("R (Recovered): No longer sick and immune to the disease."),
                html.P("Nodes having < 5 connections will have inner connections")
                
            ], style={'display': 'flex', 'flex-direction': 'column', 'padding': '20px', 
                      'background-color': '#222', 'border-radius': '10px'}),

            # Second part: Node click data and status section
            html.Div([
                html.P([f"Node ID",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="To observe selected individual connections by id")]),
                html.Div([
                dcc.Input(id='node-input', type='number', value=1,
                          style={'margin-bottom': '15px', 'width': '100px', 'height': '25px', 'font-size': '15px'}),
                dbc.Button(
                    'Reset View',
                    id='reset-button',
                    n_clicks=0,
                    style={
                        'margin-left': '10px',
                        'margin-bottom': '2px',
                        'font-size': '15px',  # Keep your font size
                        'height': '27px',
                        'width': '100px',
                        'padding':'3px 10px'
                    },
                    className='btn btn-primary',  # Bootstrap primary button style
                    size='md'                     # Medium size button (optional)
                )],style={'display': 'inline-block'}),
                

                
                html.P([f"Day Selection",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="To select a day of the simulation")]),
                dcc.Input(id='slider-input', type='number', value=1,
                          style={'margin-bottom': '15px', 'width': '100px', 'height': '25px', 'font-size': '15px'}),
                dcc.Slider(id='slider-1', min=1, max=1, step=1, value=1,
                           tooltip={"placement": "bottom", "always_visible": True}),          
                html.Div(id='click-node-data', style={'margin-top': '15px','margin-bottom': '15px', 'color': 'white', 'font-size': '15px'}),
                html.Div(id='status-data', style={'margin-bottom': '15px', 'color': 'white', 'font-size': '15px'}),
                
            ], style={'padding': '20px', 'background-color': '#222', 'border-radius': '10px', 'margin-top': '15px'}),

        ], className="left-panel", style={'flex': '1.1', 'padding': '20px'}),

        # Right panel
        html.Div([
            # First Cytoscape Network
            html.H3("Visualizing Network progression", style={'margin-bottom': '15px', 'color': 'white'}),
            html.P(id='animation-day', children='Current Day: {current_day}',
                   style={'margin-top': '15px', 'margin-bottom': '15px', 'color': 'white', 'font-size': '15px'}),

            cyto.Cytoscape(
                id='animated-network',
                elements=[],
                layout={'name': 'concentric', 'animate': False, 'minNodeSpacing': 30, 'avoidOverlap': True},
                maxZoom=1,
                style={'width': '100%', 'height': '80vh', 'margin-bottom': '3vh'}
            ),
            # Second Cytoscape Network
            html.H3("Network Exploration", style={'margin-bottom': '15px', 'color': 'white'}),
            dcc.Loading(
                id="loading-cytoscape-1",
                type="circle",
                children=[
                    cyto.Cytoscape(
                        id='cytoscape',
                        elements=[],
                        layout={'name': 'concentric', 'animate': True, 'minNodeSpacing': 30, 'avoidOverlap': True},
                        maxZoom=1,
                        style={'width': '100%', 'height': '80vh', 'margin-bottom': '3vh'},
                    )
                ]
            ),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
            # Additional Graphs
            html.Div([
                dcc.Graph(id='plotly-graph1', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph2', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph3', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph4', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph5', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph6', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph7', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph8', style={'height': '80vh', 'margin-bottom': '1vh'}),
                dcc.Graph(id='plotly-graph9', style={'height': '80vh', 'margin-bottom': '1vh'}),
                html.H3("Vaccination Impact and Contact Patterns Across Age Groups", style={'margin-bottom': '15px', 'color': 'white'}),
                generate_vaccination_impact_contact_patterns_table(),
                dbc.Alert(id='tbl_out'),
                html.H3("Age Group Contact Matrix", style={'margin-bottom': '15px', 'color': 'white'}),
                generate_contact_matrix_table(),
                dbc.Alert(id='contact-matrix-table-out'),
                dbc.Alert(
                    children=[
                        "Reference:",
                        html.Br(),
                        "- Age Group distribution By Country: ", 
                        html.A(
                            'Link',  # Link text
                            href='https://ourworldindata.org/grapher/population-by-five-year-age-group',  # URL to navigate to
                            target="_blank"  # Open the link in a new tab
                        ),
                        html.Br(),
                        "- Connections by age group (Mean Contacts/Standard Deviation): ",
                        html.A(
                            'Link',  # Link text
                            href='https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0050074&s=09',  # URL to navigate to
                            target="_blank"  # Open the link in a new tab
                        ),
                        html.Br(),
                        "- Vaccine Affecting infection rate (Infection Rate Reduction): ",
                        html.A(
                            'Link',  # Link text
                            href='https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(21)00448-7/fulltext',  # URL to navigate to
                            target="_blank"  # Open the link in a new tab
                        ),
                        html.Br(),
                        "- Age Group Contact Matrix: ",
                        html.A(
                            'Link',  # Link text
                            href='https://www.nature.com/articles/s41598-021-94609-3',  # URL to navigate to
                            target="_blank"  # Open the link in a new tab
                        ),
                    ],
                    id='tbl_references',
                    color="info"
                ),
                # Modal (Popup window) content
                html.Div(
                    id='modal',
                    children=[
                        html.Div([
                            # Close button at the top-right corner
                            html.Button(
                                'X', 
                                id='close-modal-btn', 
                                n_clicks=0, 
                                style={
                                    'position': 'fixed',  # Fixed position relative to the viewport
                                    'top': '10px',
                                    'right': '10px',
                                    'border': 'none',
                                    'background': 'transparent',
                                    'font-size': '24px',
                                    'color': 'red',
                                    'cursor': 'pointer',
                                    'font-weight': 'bold'
                                }
                            ),
                            html.H2("Comparison"),
                            # Grid layout for graphs (2 columns)
                            html.Div([
                                html.Div([
                                    html.H3("Previous", style={'text-align': 'center', 'margin-bottom': '10px'}),
                                    html.Div(id='prevVer', style={'text-align': 'center'}),
                                    dcc.Graph(id='popup-prevGraph1',style={'width': '675px'}),  
                                    dcc.Graph(id='popup-prevGraph2',style={'width': '675px'}),
                                    dcc.Graph(id='popup-prevGraph3',style={'width': '675px'}),
                                    dcc.Graph(id='popup-prevGraph4',style={'width': '675px'}),
                                    dcc.Graph(id='popup-prevGraph5',style={'width': '675px'}),
                                ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '10px'}),  # First column

                                html.Div([
                                    html.H3("Current", style={'text-align': 'center', 'margin-bottom': '10px'}),
                                    html.Div(id='currVer', style={'text-align': 'center'}),
                                    dcc.Graph(id='popup-currGraph1',style={'width': '675px'}),  
                                    dcc.Graph(id='popup-currGraph2',style={'width': '675px'}),
                                    dcc.Graph(id='popup-currGraph3',style={'width': '675px'}),
                                    dcc.Graph(id='popup-currGraph4',style={'width': '675px'}),
                                    dcc.Graph(id='popup-currGraph5',style={'width': '675px'}),
                                ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '10px'}),  # Second column
                            ], style={'display': 'flex', 'gap': '20px', 'justify-content': 'space-between','overflow': 'hidden'}),  # Two-column grid
                        ], style={'padding': '20px', 'background-color': 'white', 'position': 'relative'})
                    ],
                    style={
                        'display': 'none',  # Initially hidden
                        'position': 'fixed',
                        'top': '50%',  # Center the modal vertically
                        'left': '50%',  # Center the modal horizontally
                        'transform': 'translate(-50%, -50%)',  # Adjust to center properly
                        'width': '100%',  # Set the width of the modal (adjust as needed)
                        'max-width': '1420px',  # Max width for large screens
                        'height': 'auto',  # Allow height to adjust based on content
                        'max-height': '90vh',  # Set the maximum height to the viewport height
                        'background-color': 'rgba(0, 0, 0, 0.5)',  # Semi-transparent background
                        'justify-content': 'center',
                        'align-items': 'center',
                        'z-index': '1000',
                        'border-radius': '10px',
                        'overflow-x': 'hidden',  # Disable horizontal scrolling
                        'overflow-y': 'hidden',  # Enable vertical scrolling for the outer modal
                    }
                )
  
            ], style={'display': 'flex', 'flex-direction': 'column'}),
        ],
        className="right-panel", 
        style={'flex': '4', 'margin-top':'20px','padding': '20px', 'background-color': '#222', 'border-radius': '10px', 'height': '662vh'}),  # Adjust flex and height here

    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'height': '100vh'}),
    
], style={'background-color': '#121212',  'height': '675vh'})




@app.callback(
    [Output('slider-1', 'max'),
     Output('slider-1', 'marks'),
     Output('slider-input', 'min'),
     Output('slider-input', 'max')],
    Input('day-input', 'value')
)
def update_slider_based_on_days(days):
    """
    Updates the Day Selection sliders' range and labels based on the number of simulation days.

    This callback dynamically adjusts the properties of the day selection sliders (`slider-1` and 
    `slider-input`) in a Dash application based on the user-provided number of simulation days 
    (`day-input`).

    Parameters:
    - days (int): The number of simulation days entered by the user in the 'day-input' field. 
      If `days` is not provided, invalid, or less than 1, default values are used.

    Returns:
    - tuple:
      1. int: The maximum value of the day selection slider (`slider-1`).
      2. dict: Marks for the day selection slider, containing labels for the minimum (1) and 
               maximum (`days`) values.
      3. int: The minimum value for the day selection input slider (`slider-input`), always 1.
      4. int: The maximum value for the day selection input slider (`slider-input`), same as `days`.

    Notes:
    - If `days` is invalid or less than 1, the function defaults to setting the slider range to 1.
    - The `marks` dictionary includes labels for only the minimum and maximum slider values 
      to keep the interface clean.
    - Errors in the input (e.g., non-integer or negative values) are handled gracefully by returning defaults.

    """

    if days is None or days <= 0:
        return 1, {1: {'label': '1'}, 1: {'label': '1'}}, 1, 1  # Default case with min and max

    try:
        days = int(days)

        # Create marks for min and max values only
        marks = {
            1: {'label': '1'},     # Min label
            days: {'label': str(days)}  # Max label
        }

        return days, marks, 1, days

    except (ValueError, TypeError):
        return 1, {1: {'label': '1'}, 1: {'label': '1'}}, 1, days  # Return empty marks on error

@app.callback(
    Output('slider-1', 'value'),
    Input('slider-input', 'value'),
    State('slider-1', 'max')
)
def update_slider_value(input_value, max_value):
    """
    Updates the value of the day selection slider ('slider-1') based on the user's input in the day selection field ('slider-input').

    This callback ensures that the slider value reflects the user's input while remaining within the valid range of days,
    which is defined by the slider's maximum value.

    Parameters:
    - input_value (int): The day value entered by the user in the day selection field ('slider-input').
    - max_value (int): The maximum allowable day value for the day selection slider ('slider-1').

    Returns:
    - int: The updated value for the day selection slider ('slider-1').
        - If the input value is valid and within the range [1, max_value], it is returned.
        - If the input value is invalid, out of range, or missing, the slider value defaults to 1.

    Notes:
    - The valid range for the slider is between 1 and `max_value`, inclusive.
    - If `input_value` or `max_value` is None, or if an exception occurs (e.g., invalid type), the slider resets to 1.

    """

    if input_value is None or max_value is None:
        return 1
    
    try:
        value = int(input_value)
        if 1 <= value <= max_value:
            return value
        else:
            return 1 
    except (ValueError, TypeError):
        return 1
    
# Callback to update the input based on the slider value
@app.callback(
    Output('slider-input', 'value'),
    Input('slider-1', 'value')
)
def update_input(slider_value):
    """
    Updates the value of the day selection field ('slider-input') based on the value of the day selection slider ('slider-1').

    This callback ensures that the field reflects the current value selected by the user on the slider.

    Parameters:
    - slider_value (int): The current value of the day selection slider ('slider-1').

    Returns:
    - int: The updated value for the day selection field ('slider-input').

    Notes:
    - The callback directly synchronizes the field with the slider value, ensuring a seamless user experience.
    - The slider value is assumed to always be valid as it is constrained by the slider's range.

    """
    return slider_value



@app.callback(
    [Output('node-input', 'min'),
     Output('node-input', 'max')],
    Input('population-input', 'value')
)
def update_slider_based_on_days(population):
    """
    Updates the minimum and maximum values for the node selection input field based on the population size.

    This callback dynamically adjusts the range of the `node-input` field in a Dash application 
    based on the user-provided population size (`population-input`).

    Parameters:
    - population (int): The population size entered by the user in the 'population-input' field.
      If `population` is not provided or invalid, default values are used.

    Returns:
    - tuple:
      1. int: The minimum value for the `node-input` field, always set to 1.
      2. int: The maximum value for the `node-input` field, equivalent to the population size.

    Notes:
    - If `population` is not provided, invalid, or results in an error (e.g., non-integer value), 
      the function defaults to a range of 1 to 1.
    - This ensures that the `node-input` field remains consistent with the total number of nodes 
      in the simulation, which is defined by the population size.

    Example:
    Input:
        population-input = 500
    Output:
        (1, 500)
    """
    if population is None:
        return 1, 1
    try:
        population = int(population)
        return 1, population

    except (ValueError, TypeError):
        # Default values if there's an error in input
        return 1, 1
    




def processNetwork(network, selected_node, checkbox):
    """
    Update the nodes and edges in the Cytoscape graph based on the given network,
    optionally filtering the elements based on user input.

    Parameters:
    - network: The network object containing nodes and their connections.
    - selected_node: Node ID selected by the user (optional).
    - checkbox: List of checkbox options selected by the user (e.g., 'removeOthers').

    Logic:
    1. Generates a list of nodes from the network object, sorted by their integer IDs.
    2. Creates edges based on the node connections.
    3. Optionally filters nodes and edges:
       - If 'removeOthers' is in the checkbox, shows only the selected node and its connections.
       - Otherwise, displays the full network but highlights connections of the selected node.

    Returns:
    - A list of elements (nodes and edges) for the Cytoscape graph.
    """

    # Mapping status codes to descriptive labels
    statusMap = {
        'S': 'Susceptible',
        'P': 'Presymptomatic',
        'A': 'Asymptomatic',
        'I': 'Infectious',
        'R': 'Recovered',
    }

    elements = []  # List to store nodes and edges for Cytoscape

    # Get all nodes from the network
    nodes = network.getNodes()

    # Sort nodes by their integer IDs for consistent order
    sorted_keys = sorted(nodes.keys(), key=lambda k: int(k))  # Convert string keys to integers
    sorted_nodes_dict = {key: nodes[key] for key in sorted_keys}  # Create a sorted dictionary of nodes

    # Loop through each node and generate its corresponding Cytoscape element
    for node in sorted_nodes_dict.values():
        # Get connections for the current node and sort them
        nodeConnections = node.getConnections()
        connections = sorted([str(nodeConnection) for nodeConnection in nodeConnections], key=int)
        connections_str = ', '.join(connections)  # Create a comma-separated string of connections

        # Generate the node element for Cytoscape
        # Node {'data': {'id': '190', 'label': 'Node 190', 'status': 'Susceptible', 'age': '52', 'S': '1', 'P': '0', 'A': '0', 'I': '0', 'R': '0', 'day': 1, 'connections': '1'}}

        elements.append({
            'data': {
                'id': str(node.id),                          # Node ID
                'label': f'Node {node.id}',                  # Node label
                'age': str(node.age),                        # Age of the node
                'status': statusMap.get(node.status),        # Status (e.g., Susceptible, Infectious)
                'vaccinated': 'Yes' if node.vaccinated else 'No',  # Vaccination status
                'S': str(round(node.S * 100, 1)) + '%',      # Susceptible percentage
                'P': str(round(node.P * 100, 1)) + '%',      # Presymptomatic percentage
                'A': str(round(node.A * 100, 1)) + '%',      # Asymptomatic percentage
                'I': str(round(node.I * 100, 1)) + '%',      # Infectious percentage
                'R': str(round(node.R * 100, 1)) + '%',      # Recovered percentage
                'day': node.day,                             # Simulation day
                'connections': connections_str               # List of connections as a string
            }
        })

        # Generate the edge elements for Cytoscape based on the node's connections
        # Edge shown in the network {'data': {'source': '190', 'target': '1'}
        for connection in connections:
            elements.append({
                'data': {
                    'source': str(node.id),      # Source node ID
                    'target': str(connection)    # Target node ID
                }
            })

    # If a node is selected, filter the elements based on the selected node and checkbox options
    if selected_node is not None:
        if 'removeOthers' in checkbox:  # If 'removeOthers' is checked
            # Get the connections of the selected node
            nodeConnections = sorted_nodes_dict.get(str(selected_node)).getConnections()
            connections = [str(nodeConnection) for nodeConnection in nodeConnections]
            connections.append(str(selected_node))  # Include the selected node itself

            # Filter elements to show only the selected node and its connections
            elements = [
                element for element in elements if 
                ('id' in element['data'] and  # Keep nodes that are in the selected node's network
                 element['data']['id'] in connections) or 
                ('source' in element['data'] and  # Keep edges connected to the selected node
                 (element['data']['source'] == str(selected_node) or 
                  element['data']['target'] == str(selected_node)))
            ]
        else:  # If 'removeOthers' is not checked
            # Show all nodes but highlight edges connected to the selected node
            elements = [
                element for element in elements if 
                ('source' not in element['data'] or  # Keep all nodes
                 (element['data']['source'] == str(selected_node) or  # Highlight edges of the selected node
                  element['data']['target'] == str(selected_node)))
            ]

    # Return the updated list of elements for Cytoscape
    return elements



@app.callback(
    [Output('cytoscape', 'elements'), 
     Output('generate-button', 'n_clicks'), 
     Output('error-popup', 'displayed'), 
     Output('error-popup', 'message'), 
     Output('prevVer', 'children'), 
     Output('currVer', 'children')],
    [Input('generate-button', 'n_clicks'),
     Input('node-input', 'value'),
     Input('slider-1', 'value'),
     Input('checkbox-list', 'value')],
    [State('input-age-1', 'value'),
     State('input-age-2', 'value'),
     State('input-age-3', 'value'),
     State('input-age-4', 'value'),
     State('input-age-5', 'value'),
     State('input-age-6', 'value'),
     State('input-age-7', 'value'),
     State('input-age-8', 'value'),
     State('seed-input', 'value'),
     State('reproNum-input', 'value'),
     State('population-input', 'value'),
     State('day-input', 'value'),
     State('affected-input', 'value'),
     State('interventionDay-input', 'value'),
     State('vacPercent-input', 'value'),
     State('connection-radio', 'value')
    ]
)
def generateAndUpdateNetwork(n_clicks, selected_node, slider_value, checkbox, age1, age2, age3, age4, age5, age6, age7, age8, seed, reproNum, population, days, affected, interventionDay, vacPercent, radio):
    """
    Callback function that generates and updates a contact network based on user input. 
    It processes the user inputs, validates them, runs an external simulation, and updates the network visualization accordingly.

    Parameters:
        n_clicks (int): Number of times the "Generate" button has been clicked.
        selected_node (str): Node selected in the Cytoscape network.
        slider_value (int): Value from the slider to determine the day of the network to display.
        checkbox (list): List of selected checkboxes indicating which parameters are enabled (e.g., age, vaccination, isolation).
        age1, age2, age3, age4, age5, age6, age7, age8 (float): Percentage composition of different age groups in the population.
        seed (int): Seed for the random number generator.
        reproNum (float): Reproduction number for the simulation.
        population (int): Total population size.
        days (int): Number of days for the simulation.
        affected (int): Number of people initially infected.
        interventionDay (int): The day vaccination or isolation interventions begin.
        vacPercent (int): The daily vaccination percentage.
        radio (str): Selected radio button option.

    Returns:
        tuple: 
            - elements (list): Processed Cytoscape elements for rendering the network.
            - n_clicks (int): Reset the "Generate" button click count to 0.
            - displayed (bool): Boolean value to indicate if the error popup should be displayed.
            - message (str): Error or status message to display in the popup.
            - prevVer (list): Version details of the previous simulation.
            - currVer (list): Version details of the current simulation.
    """
    global dailyNetwork, infectionGraph, populationPie, stackBarPlot, infectionRatePlot, degreeVsInfectionPlot, truePositiveRatePlot, current_day, overallInfectionRate, dayInfectionRateList, avgDailyConnectionsList, prevVer, currVer

    # Handle "Generate" button click
    if n_clicks > 0:
        # Validate age composition if the 'age' option is selected
        if 'age' in checkbox and sum([age1, age2, age3, age4, age5, age6, age7, age8]) != 100:
            return [], 0, True, 'Ensure Age composition = 100%', prevVer, currVer

        # Validate inputs for 'vaccination' and 'isolate' options
        if 'vaccination' in checkbox and (interventionDay is None or vacPercent is None):
            return [], 0, True, 'Check for empty inputs', prevVer, currVer
        if 'isolate' in checkbox and (interventionDay is None or vacPercent is None):
            return [], 0, True, 'Check for empty inputs', prevVer, currVer

        # Validate essential inputs
        if None in {seed, reproNum, population, days, affected}:
            return [], 0, True, 'Check for empty inputs', prevVer, currVer

        # Set default values if certain options are not selected
        if 'age' not in checkbox:
            age1 = age2 = age3 = age4 = age5 = age6 = age7 = age8 = 12.5  # Equal distribution by default

        try:
            # Reset and rename files for storing status
            reset_file()
            renameFile()
            # Read the current version status from the file
            with open(statusPath, 'r') as file:
                status = json.load(file)
            status['prevVer'] = status['currVer']  # Update previous version

            # Prepare current version details
            currVer = [f'Seed: {seed}, Reproduction Number: {reproNum}, Population: {population}, Day: {days}, Infected Population: {affected}']
            if 'isolate' in checkbox:
                currVer.append(f'Intervention Day: {interventionDay}')
            if 'vaccination' in checkbox:
                currVer.append(f'Intervention Day: {interventionDay}, Vaccination Rate: {vacPercent}')
            if 'age' in checkbox:
                age_group_details = 'Composition of age group:'
                if age1 != 0:
                    age_group_details += f' (0-9): {age1}%,'
                if age2 != 0:
                    age_group_details += f' (10-19): {age2}%,'
                if age3 != 0:
                    age_group_details += f' (20-29): {age3}%,'
                if age4 != 0:
                    age_group_details += f' (30-39): {age4}%,'
                if age5 != 0:
                    age_group_details += f' (40-49): {age5}%,'
                if age6 != 0:
                    age_group_details += f' (50-59): {age6}%,'
                if age7 != 0:
                    age_group_details += f' (60-69): {age7}%,'
                if age8 != 0:
                    age_group_details += f' (>70): {age8}%,'
                currVer.append(age_group_details[:-1])  # Remove trailing comma
            status['currVer'] = currVer
            currVer = [html.P(f"{line}", style={'word-wrap': 'break-word','color':'black'}) for line in currVer]
            prevVer = [html.P(f"{line}", style={'word-wrap': 'break-word','color':'black'}) for line in status['prevVer']]

            # Save updated status to the file
            with open(statusPath, 'w', encoding='utf-8') as file:
                json.dump(status, file, indent=4)

            # Execute external program with provided inputs
            proportionList = [str(age1), str(age2), str(age3), str(age4), str(age5), str(age6), str(age7), str(age8)]
            
            result = subprocess.run(
                ['python', templatePath, str(seed), str(reproNum), str(population), str(days), str(affected), str(interventionDay), str(vacPercent), str(radio)] + proportionList + checkbox,
                capture_output=True,
                text=True,
                check=True
            )
            output_data = json.loads(result.stdout.strip())
            
            # Update global variables with output from the external program
            encoded_network = output_data.get('dailyNetwork')
            infectionGraph = pio.from_json(output_data.get('infectionGraph'))
            populationPie = pio.from_json(output_data.get('populationPie'))
            stackBarPlot = pio.from_json(output_data.get('stackBarPlot'))
            infectionRatePlot = pio.from_json(output_data.get('infectionRatePlot'))
            degreeVsInfectionPlot = pio.from_json(output_data.get('degreeVsInfectionPlot')) 
            truePositiveRatePlot = pio.from_json(output_data.get('truePositiveRatePlot'))
            overallInfectionRate = output_data.get('overallInfectionRate')
            dayInfectionRateList = output_data.get('dayInfectionRateList')
            avgDailyConnectionsList = list(map(float, output_data.get('avgDailyConnectionsList')))
            
            dailyNetwork = jsonpickle.decode(encoded_network)
            network = dailyNetwork.getNetworkByDay('1')  # Access Day 1's network
            current_day = 1
            # Process network for Cytoscape elements
            elements = processNetwork(network, selected_node, checkbox)

        except subprocess.CalledProcessError as e:
            return [], 0, True, f"Error in external program: {e.stderr}", prevVer, currVer
        except Exception as e:
            return [], 0, True, f"An error occurred: {str(e)}", prevVer, currVer

    # Handle slider adjustment (for already generated networks)
    elif dailyNetwork is not None:
        network = dailyNetwork.getNetworkByDay(str(slider_value))
        if network is None:
            return [], 0, True, "Generate Network to Start", prevVer, currVer
        elements = processNetwork(network, selected_node, checkbox)

    else:
        elements = []  # Default to an empty list if no conditions are met

    # Return updated elements and reset the generate button's click count
    return elements, 0, False, '', prevVer, currVer


def splitConnections(connections_str, items_per_line=8):
    """
    Splits a comma-separated connections string into multiple lines, 
    with a specified number of items per line.

    Parameters:
        connections_str (str): A comma-separated string of connections (e.g., '1, 2, 3, 4, 5, ...').
        items_per_line (int, optional): The number of items to display per line. Defaults to 8.

    Returns:
        list: A list of strings, each representing a line of connections with up to `items_per_line` items.
    
    Example:
        splitConnections('1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11', 4)
        Returns:
        [
            '1, 2, 3, 4',
            '5, 6, 7, 8',
            '9, 10, 11'
        ]
    """
    # Split the connections string into a list of individual items based on the comma separator
    connections_list = connections_str.split(', ')
    
    # Initialize an empty list to store the lines of connections
    lines = []
    
    # Create lines by slicing the list of connections into chunks of size `items_per_line`
    for i in range(0, len(connections_list), items_per_line):
        # Join the items in the current slice with a comma and space, and add it to the lines list
        line = ', '.join(connections_list[i:i + items_per_line])
        lines.append(line)
    
    # Return the list of formatted lines
    return lines
     
@app.callback(
    [Output('click-node-data', 'children'), Output('plotly-graph6', 'figure')],
    [Input('cytoscape', 'tapNodeData'), Input('cytoscape', 'elements')]
)
def displayClickData(data, elements):
    """
    Callback function triggered when a node is clicked in the Cytoscape network.
    Displays detailed information about the clicked node and updates a plot showing 
    the frequency of ages of connected nodes.

    Parameters:
        data (dict): Data of the clicked node, including attributes like 'id', 'label', 'status', 'age', etc.
        elements (list): List of all elements in the Cytoscape network.

    Returns:
        tuple: 
            - HTML Div element with detailed node information.
            - Plotly figure showing the age distribution of connected nodes.
    """
    global indiAgeFreqPlot
    
    # Define the color mapping for different status states
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }

    if data:
        # Extract the connections string from the clicked node's data
        connections_str = data['connections']
        
        # Split the connections string into multiple lines for better readability
        connection_lines = splitConnections(connections_str)
        
        # Convert the connections string into a list of connected node IDs
        connectionsList = connections_str.split(', ')
        
        if elements:
            # Initialize an empty list to store ages of connected nodes
            connectionsAgeList = []
            
            # Iterate through all elements in the network
            # node data: {'data': {'id': '190', 'label': 'Node 190', 'status': 'Susceptible', 'age': '52', 'S': '1', 'P': '0', 'A': '0', 'I': '0', 'R': '0', 'day': 1, 'connections': '1'}}
            for element in elements:
                if 'age' in element['data']:  # Check if the element has age information
                    # If the element is in the connections list, add its age to the list
                    if element['data']['id'] in connectionsList:
                        connectionsAgeList.append(int(element['data']['age']))
            
            # Generate the individual age frequency plot for connected nodes
            indiAgeFreqPlot = plotIndiConnAgeGroup(connectionsAgeList, data['id'])

            # Build the HTML Div output displaying detailed information about the clicked node
            return html.Div([
                # Display node information with appropriate icons and values
                html.P([html.I(className="bi bi-calendar pe-1", style={"color": 'white', "margin-right": "5px"}), 
                        f"Day: {data['day']}"]),
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": 'white', "margin-right": "5px"}), 
                        f"Node: {data['label'][4:]}"]),
                html.P([html.I(className="bi bi-file-person-fill pe-1", style={"color": 'white', "margin-right": "5px"}), 
                        f"Age: {data['age']}"]),    
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get(data['status']), "margin-right": "5px"}), 
                        f"Status: {data['status']}"]),
                html.P([html.I(className="fas fa-syringe", style={"color": 'white', "margin-right": "5px"}), 
                        f"Vaccinated: {data['vaccinated']}"]),
                # Display probabilities for the node transitioning to different states
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Susceptible'), "margin-right": "5px"}), 
                        f"Probabilty to Susceptible State: {data['S']}"]), 
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Presymptomatic'), "margin-right": "5px"}), 
                        f"Probabilty to Presymptomatic State: {data['P']}"]),
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Asymptomatic'), "margin-right": "5px"}), 
                        f"Probabilty to Asymptomatic State: {data['A']}"]),
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Infectious'), "margin-right": "5px"}), 
                        f"Probabilty to Infected State: {data['I']}"]),
                html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Recovered'), "margin-right": "5px"}), 
                        f"Probabilty to Recovered State: {data['R']}"]),
                # Display connections in multiple lines for readability
                *[html.P(f"Connections: {line}", style={'word-wrap': 'break-word'}) if i == 0 else html.P(f"{line}", style={'word-wrap': 'break-word'}) 
                for i, line in enumerate(connection_lines)]
            ], style={'max-width': '100vh', 'font-size': '14px', 'margin-bottom': '15px'}), indiAgeFreqPlot 

    # Return default message if no node is clicked or no data is available
    return "Click a node in Network Exploration for details", {'data': [], 'layout': {'title': 'Graph Not Available'}}






@app.callback(
    Output('status-data', 'children'),  # Output where the status data will be displayed
    [Input('cytoscape', 'elements')],  # Input: cytoscape elements (network nodes)
    [State('slider-input', 'value'),
     State('day-input', 'value')]   # State: current value of the slider (Day)
)
def display_nodes_status(elements, day, totalDays):
    """
    Callback function to display the status of nodes in the network based on their 
    current state (Susceptible, Presymptomatic, Asymptomatic, Infectious, or Recovered) 
    and their vaccination status.

    The function processes the list of elements (nodes) from the cytoscape graph, 
    calculates various statistics (such as average connections, vaccinated count, 
    unvaccinated count, and infection rates), and returns HTML content that displays 
    the status of nodes, as well as other related statistics like the infection rate 
    for the current day and overall.

    Parameters:
        elements (list): List of dictionaries representing the nodes in the network. 
                          Each dictionary contains node data such as 'id', 'status', 
                          'vaccinated', and 'connections'.
        day (int): The current day value from the slider, used to display the infection rate.

    Returns:
        html.Div: An HTML component containing paragraphs that display the status of nodes 
                  categorized by their health status and additional information such as 
                  average connections, infection rates, and vaccination status.
        
    If no elements are provided (i.e., no nodes in the network), the function returns 
    a default message prompting the user to generate a network to see the status.
    """
    global countPlot, overallInfectionRate, dayInfectionRateList, avgDailyConnectionsList
    # Define a color map for each status
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }   
    if elements:  # Check if elements (nodes) are available
        # Lists to store nodes based on their status
        sList = []
        pList = []
        aList = []
        iList = []
        rList = []
        vaccinatedCount = 0
        unVaccinatedCount = 0
        count = 0
        # List of the number of connections each node has
        nodeConnectionsCount = []

        # node {'data': {'id': '190', 'label': 'Node 190', 'status': 'Susceptible', 'age': '52', 'S': '1', 'P': '0', 'A': '0', 'I': '0', 'R': '0', 'day': 1, 'connections': '1'}}
        for element in elements:  # Iterate through each node in the elements
            # Check if the node contains status information
            if 'status' in element['data']:
                # Categorize nodes based on their status
                if element['data']['status'] == 'Susceptible':
                    sList.append(element['data']['id'])
                elif element['data']['status'] == 'Presymptomatic':
                    pList.append(element['data']['id'])
                elif element['data']['status'] == 'Asymptomatic':
                    aList.append(element['data']['id'])
                elif element['data']['status'] == 'Infectious':
                    iList.append(element['data']['id'])   
                else:
                    rList.append(element['data']['id'])  # Add to Recovered list

                # Count vaccinated vs. unvaccinated nodes
                if element['data']['vaccinated'] == 'Yes':  
                    vaccinatedCount += 1
                else:
                    unVaccinatedCount += 1
                
                # Count the number of connections a node has
                nodeConnectionsNum = len(element['data']['connections'].split(', ')) 
                nodeConnectionsCount.append(nodeConnectionsNum)   
                count += 1
        
        # Generate plot of node connection counts
        countPlot = plotCountConnections(nodeConnectionsCount)    
        avgConnections = avgDailyConnectionsList[day-1]      # Calculate average number of connections
        overallConnections = round(sum(avgDailyConnectionsList)/totalDays,2)
        # Split the connections into manageable lines
        sList_lines = splitConnections(', '.join(sList))
        pList_lines = splitConnections(', '.join(pList))
        aList_lines = splitConnections(', '.join(aList))
        iList_lines = splitConnections(', '.join(iList))
        rList_lines = splitConnections(', '.join(rList))

        # Build the HTML output to display status data
        return html.Div([
            html.P([html.I(className="bi bi-people-fill pe-1", style={"color": "white", "margin-right": "5px"}),
                f"Overall Population status for Day: {day}"]),
            html.P([html.I(className="bi bi-link pe-1", style={"color": "white", "margin-right": "5px"}),
                f"Average Connections: {str(avgConnections)}"]),  
            html.P([html.I(className="bi bi-link pe-1", style={"color": "white", "margin-right": "5px"}),
                f"Overall Average Connections: {str(overallConnections)}"]),  
            html.P([html.I(className="fa-solid fa-chart-line", style={"color": "white", "margin-right": "5px"}),
                f"Infection Rate At Day {day}: {dayInfectionRateList[day-1]}%"]),  
            html.P([html.I(className="fa-solid fa-chart-line", style={"color": "white", "margin-right": "5px"}),
                f"Overall Infection Rate: {overallInfectionRate}%"]),      
            html.P([html.I(className="fa-solid fa-syringe", style={"color": "white", "margin-right": "5px"}),
                f"Vaccinated: {vaccinatedCount}"]),
            html.P([html.I(className="bi bi-shield-x", style={"color": "white", "margin-right": "5px"}),
                f"Unvaccinated: {unVaccinatedCount}"]),    
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Susceptible'), "margin-right": "5px"}),
                f"Status: Susceptible"]), 
            *[html.P(f"Nodes: {line}") if i == 0 else html.P(f"{line}") for i, line in enumerate(sList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Presymptomatic'), "margin-right": "5px"}),
                f"Status: Presymptomatic"]),
            *[html.P(f"Nodes: {line}") if i == 0 else html.P(f"{line}") for i, line in enumerate(pList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Asymptomatic'), "margin-right": "5px"}),
                f"Status: Asymptomatic"]),
            *[html.P(f"Nodes: {line}") if i == 0 else html.P(f"{line}") for i, line in enumerate(aList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Infectious'), "margin-right": "5px"}),
                f"Status: Infected"]),
            *[html.P(f"Nodes: {line}") if i == 0 else html.P(f"{line}") for i, line in enumerate(iList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Recovered'), "margin-right": "5px"}),
                f"Status: Recovered"]),
            *[html.P(f"Nodes: {line}") if i == 0 else html.P(f"{line}") for i, line in enumerate(rList_lines)]
        ])

    return "Generate network to see nodes status"  # Default message when no nodes are selected

            
                     
@app.callback(
    Output('cytoscape', 'stylesheet'),
    Input('cytoscape', 'elements')
)
def update_stylesheet(elements):
    """
    Callback function to update the stylesheet of a Cytoscape network based on the 
    'status' attribute of each node. The function assigns different colors to nodes 
    based on their status (e.g., Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered)
    and applies styles for edges and labels.

    The function iterates over the elements (nodes) in the network and applies specific 
    styles for each node based on its 'status'. Nodes with different statuses are given 
    different background colors, and the text content is styled with a white font and black outline. 
    A default style is applied to edges, giving them a grey color and a straight line style.

    Parameters:
        elements (list): List of dictionaries representing the elements (nodes) in the 
                          network. Each dictionary contains node data such as 'id' and 'status'.

    Returns:
        list: A list of styles (CSS rules) to be applied to the Cytoscape network. This list 
              includes styles for nodes (e.g., background color based on status) and edges 
              (e.g., line color and width).
    """
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }
    
    # Initial stylesheet for nodes with basic label styling
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'content': 'data(label)',  # Display the label
                'font-size': '12px',
                'color': 'white',          # Text color
                'text-valign': 'center',   # Align text vertically
                'text-halign': 'center',   # Align text horizontally
                'text-outline-color': 'black',  # Outline color for text
                'text-outline-width': '2px'     # Outline width for text
            }
        }
    ]
    
    # Loop over elements to apply styles based on the 'status' attribute
    for element in elements:
        if 'data' in element and 'status' in element['data']:
            # Apply a style based on the 'status'
            color = statusColourMap.get(element['data']['status'])
            stylesheet.append({
                'selector': f'node[id = "{element["data"]["id"]}"]',
                'style': {
                    'background-color': color,
                    'border-width': '2px',
                    'border-color': color
                }
            })

    # Style for edges
    stylesheet.append({
        'selector': 'edge',
        'style': {
            'line-color': 'grey',
            'curve-style': 'straight',
            'width': 2
        }
    })

    return stylesheet



@app.callback([Output('animated-network', 'elements'),
              Output('animation-day', 'children')],
              [Input('interval-component', 'n_intervals'),
               Input('cytoscape', 'elements'),
               Input('checkbox-list', 'value'),
               Input('node-input', 'value')])
def animate_network(n, elements, checkbox, selected_node):
    """
    Callback function to animate a network by updating its elements at regular intervals.
    The function retrieves the network for the current day from the `dailyNetwork` object 
    and processes it based on user-selected nodes and checkbox values. It also updates the 
    current day and resets when the last day is reached.

    Parameters:
        n (int): The number of intervals that have passed since the start. Used to trigger 
                 periodic updates of the network.
        elements (list): The current list of elements in the Cytoscape network. This is 
                         updated each time the network is animated.
        checkbox (list): A list of selected checkbox values, used to filter or adjust the 
                         network elements.
        selected_node (str): The ID of the selected node, which may influence how the 
                             network elements are processed and displayed.

    Returns:
        list: A list of elements (nodes and edges) representing the animated network for 
              the current day. If no network is available or if the daily network is not 
              generated, an error message is returned.
    """
    global dailyNetwork, current_day
    networkday = current_day
    if dailyNetwork is None:
        return [{'data': {'id': 'Error', 'label': f"Generate Network to Start"}}], f"Current Day: {networkday}"
    else:
        # Retrieve the network for the current day
        network = dailyNetwork.getNetworkByDay(str(current_day))
        if network is None:
            return [{'data': {'id': 'Error', 'label': f"Generate Network to Start"}}], f"Current Day: {networkday}"
        # Process the network based on selected node and checkbox values
        elements = processNetwork(network, selected_node, checkbox)
        if current_day == len(dailyNetwork.networks):
            current_day = 1 
        else:
            current_day += 1
    return elements, f"Current Day: {networkday}"

@app.callback(
    Output('animated-network', 'stylesheet'),
    Input('animated-network', 'elements')
)
def update_stylesheet2(elements):
    """
    Callback function to update the stylesheet for the Cytoscape network based on the 
    status attribute of the nodes. The function applies different background colors 
    to nodes based on their status (e.g., Susceptible, Presymptomatic, etc.), and 
    styles edges with a default grey color.

    Parameters:
        elements (list): A list of elements (nodes and edges) in the Cytoscape network. 
                         The function iterates over the nodes to apply styles based on 
                         their 'status' attribute.

    Returns:
        list: A list of stylesheet objects that define the visual styles for the nodes 
              and edges in the network. This includes background colors for nodes 
              based on their status and a default style for edges.
    """
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }   
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'content': 'data(label)',  # Display the label
                'font-size': '12px',
                'color': 'white',          # Text color
                'text-valign': 'center',   # Align text vertically
                'text-halign': 'center',    # Align text horizontally
                'text-outline-color': 'black',      # Outline color
                'text-outline-width': '2px'         # Outline width
            }
        }
    ]
    
    # Loop over elements to apply styles based on the 'status' attribute
    for element in elements:
        if 'data' in element and 'status' in element['data']:
            # Apply a style based on the 'status'
            color = statusColourMap.get(element['data']['status'])
            stylesheet.append({
                'selector': f'node[id = "{element["data"]["id"]}"]',
                'style': {
                    'background-color': color,
                    'border-width': '2px',
                    'border-color': color
                }
            })

    # Style for edges
    stylesheet.append({
        'selector': 'edge',
        'style': {
            'line-color': 'grey',
            'width': 2
        }
    })

    return stylesheet



@app.callback(
    Output('plotly-graph1', 'figure'),
    [Input('cytoscape', 'elements'),
     Input('slider-input', 'value')]
)
def update_graph(elements, slider_value):
    """
    Callback function to update the Plotly graph based on Cytoscape elements 
    and the selected slider value.

    This function is triggered by changes in the elements of the Cytoscape graph 
    or by adjustments to the slider input. It updates the graph to reflect the 
    infection data and includes a vertical line at the position defined by the 
    slider value.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.
        slider_value (int): The value of the slider, which determines the position 
                            of the vertical line on the graph.

    Returns:
        dict: A Plotly figure in dictionary format, which contains the data and 
              layout of the graph, including any updates such as the vertical line 
              drawn at the slider position.
    """
    global infectionGraph
    if infectionGraph is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        # Decode the Plotly graph object if it's stored as JSON
        fig = go.Figure(infectionGraph)  # make a copy of figure, without affecting it

        # Add the vertical line at the specified day_value
        if slider_value is not None:
            fig.add_vline(
                x=slider_value,  # Position of the vertical line
                line_width=3,
                line_dash="dash",
                line_color="red"
            )

        # Return the updated figure
        return fig

    

@app.callback(
    Output('plotly-graph2', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the infection rate graph based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the infection rate plot to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              infection rate plot. If the infection rate plot is not available, 
              it returns a placeholder graph with the title "Graph Not Available".
    """
    global infectionRatePlot
    if infectionRatePlot is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return infectionRatePlot

    
@app.callback(
    Output('plotly-graph3', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the population pie chart based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the population pie chart to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              population pie chart. If the pie chart is not available, it returns
              a placeholder graph with the title "Graph Not Available".
    """
    global populationPie
    if populationPie is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return populationPie

    
@app.callback(
    Output('plotly-graph4', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the stacked bar chart based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the stacked bar chart to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              stacked bar chart. If the chart is not available, it returns
              a placeholder graph with the title "Graph Not Available".
    """
    global stackBarPlot
    if stackBarPlot is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return stackBarPlot


@app.callback(
    Output('plotly-graph5', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the count plot based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the count plot to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              count plot. If the plot is not available, it returns a placeholder 
              graph with the title "Graph Not Available".
    """
    global countPlot
    if countPlot is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return countPlot

    

@app.callback(
    Output('plotly-graph7', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the distribution subplot based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It checks whether the distribution subplot is available. If it 
    is not, it calls a helper function to generate the distribution subplot 
    and returns it. Otherwise, it returns the existing distribution subplot.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              distribution subplot. If the subplot is not available, a helper 
              function is called to generate and return it.
    """
    global distributionSubPlot
    if distributionSubPlot is None:
        return plotDistributionSubPlot()
    else:
        return distributionSubPlot
    

@app.callback(
    Output('plotly-graph8', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the degreeVsInfection Plot based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the degreeVsInfection Plot to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              count plot. If the plot is not available, it returns a placeholder 
              graph with the title "Graph Not Available".
    """
    global degreeVsInfectionPlot
    if degreeVsInfectionPlot is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return degreeVsInfectionPlot
    

 
@app.callback(
    Output('plotly-graph9', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update the True Positive rate Plot based on changes to 
    the Cytoscape elements.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It updates the True Positive rate Plot to reflect the latest data, 
    returning a figure that can be displayed in the corresponding graph component.

    Parameters:
        elements (list): The elements of the Cytoscape graph, used for checking 
                         if the network has been generated.

    Returns:
        dict: A Plotly figure in dictionary format, representing the updated 
              count plot. If the plot is not available, it returns a placeholder 
              graph with the title "Graph Not Available".
    """
    global truePositiveRatePlot
    if truePositiveRatePlot is None:
        return {
            'data': [],
            'layout': {
                'title': 'Graph Not Available'
            }
        }
    else:
        return truePositiveRatePlot

@app.callback(
    [Output('popup-currGraph1', 'figure'),
     Output('popup-currGraph2', 'figure'),
     Output('popup-currGraph3', 'figure'),
     Output('popup-currGraph4', 'figure'),
     Output('popup-currGraph5', 'figure'),
     Output('popup-prevGraph1', 'figure'),
     Output('popup-prevGraph2', 'figure'),
     Output('popup-prevGraph3', 'figure'),
     Output('popup-prevGraph4', 'figure'),
     Output('popup-prevGraph5', 'figure')],
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    """
    Callback function to update multiple popup graphs based on the Cytoscape 
    elements. It reads JSON plot data from predefined paths and returns the 
    corresponding figures for the current and previous graphs.

    This function is triggered when the elements of the Cytoscape graph are 
    updated. It attempts to load the corresponding plot data from JSON files 
    for both the current and previous figures. If the plot file exists, the 
    figure is loaded; otherwise, an empty figure with a 'Graph Not Available' 
    title is returned.

    Parameters:
        elements (list): The elements from the Cytoscape graph, which can be 
                         used to check if the network has been updated or 
                         generated.

    Returns:
        tuple: A tuple containing the updated figures for the following graphs 
               in the following order:
               - Current Graph 1
               - Current Graph 2
               - Current Graph 3
               - Current Graph 4
               - Current Graph 5
               - Previous Graph 1
               - Previous Graph 2
               - Previous Graph 3
               - Previous Graph 4
               - Previous Graph 5

        If any graph figure is unavailable, an empty figure with the title 
        'Graph Not Available' is returned.
    """
 

    # Load the figure from the JSON file using the correct function
    plotJsonPathList = ['./data/currPlotResult.json','./data/currInfectionRate.json','./data/currPlotAgeGroup.json','./data/currStackBar.json','./data/currPlotCountConnections.json',
                        './data/prevPlotResult.json','./data/prevInfectionRate.json','data/prevPlotAgeGroup.json','./data/prevStackBar.json','./data/prevPlotCountConnections.json']
    currFig1 = currFig2 = currFig3 = currFig4 = currFig5 = prevFig1 = prevFig2 = prevFig3 = prevFig4 = prevFig5 =None
    
    if os.path.exists(plotJsonPathList[0]):
        currFig1 = pio.read_json(plotJsonPathList[0])
    if os.path.exists(plotJsonPathList[1]):
        currFig2 = pio.read_json(plotJsonPathList[1])
    if os.path.exists(plotJsonPathList[2]):
        currFig3 = pio.read_json(plotJsonPathList[2])
    if os.path.exists(plotJsonPathList[3]):
        currFig4 = pio.read_json(plotJsonPathList[3])
    if os.path.exists(plotJsonPathList[4]):
        currFig5 = pio.read_json(plotJsonPathList[4])    
    if os.path.exists(plotJsonPathList[5]):
        prevFig1 = pio.read_json(plotJsonPathList[5])
    if os.path.exists(plotJsonPathList[6]):
        prevFig2 = pio.read_json(plotJsonPathList[6])
    if os.path.exists(plotJsonPathList[7]):
        prevFig3 = pio.read_json(plotJsonPathList[7])
    if os.path.exists(plotJsonPathList[8]):
        prevFig4 = pio.read_json(plotJsonPathList[8])
    if os.path.exists(plotJsonPathList[9]):
        prevFig5 = pio.read_json(plotJsonPathList[9])
    

    return (
        currFig1 if currFig1 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        currFig2 if currFig2 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        currFig3 if currFig3 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        currFig4 if currFig4 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        currFig5 if currFig5 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        prevFig1 if prevFig1 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        prevFig2 if prevFig2 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        prevFig3 if prevFig3 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        prevFig4 if prevFig4 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
        prevFig5 if prevFig5 is not None else {'data': [], 'layout': {'title': 'Graph Not Available'}},
    )

@app.callback(
    Output('cytoscape', 'layout'),
    [Input('reset-button', 'n_clicks')]
)
def reset_view(n_clicks):
    """
    Callback function to reset the layout of the Cytoscape graph when the 
    reset button is clicked.

    This function is triggered when the reset button is clicked, and it 
    resets the graph's layout to the 'concentric' layout with specific 
    padding and animation settings.

    Parameters:
        n_clicks (int): The number of times the reset button has been clicked. 
                        The layout will be reset if the number of clicks is 
                        greater than 0.

    Returns:
        dict: The updated layout for the Cytoscape graph. If the reset button 
              has not been clicked, no update is made (dash.no_update).
    """
    if n_clicks > 0:
        return {
            'name': 'concentric', 
            'padding': 10,
            'animate': True,
            'animationDuration': 1000
        }
    return dash.no_update


@app.callback(
    [Output("progress", "value"), Output("progress", "label"), Output("progress", "color")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    """
    Callback function to update the progress bar on the Dash app.

    This function reads the current progress value from a status file and updates
    the progress bar value, label, and color. The progress is displayed as a percentage.
    The color of the progress bar changes based on the progress value:
        - Red (danger) for progress < 30%
        - gold (warning) for progress between 30% and 70%
        - Green (success) for progress > 70%

    Args:
        n (int): The number of intervals that have passed, used as input for the callback.

    Returns:
        tuple: A tuple containing:
            - progress (int): The updated progress value (0 to 100).
            - label (str): The progress label (e.g., "75%").
            - color (str): The color for the progress bar, which can be 'danger', 'warning', or 'success'.
    """
    try:
        # Read the current status from the file
        with open(statusPath, 'r') as file:
            progress = json.load(file)['progress']
            progress = min(progress, 100)  # Ensure progress does not exceed 100%
    except (FileNotFoundError, ValueError):
        progress = 0

    # Determine the color based on the progress value
    if progress < 30:
        color = "danger"  # Red for low progress
    elif progress < 70:
        color = "warning"  # gold for medium progress
    else:
        color = "success"  # Green for high progress

    return progress, f"{progress} %" if progress >= 5 else "", color


def reset_file():
    """
    Resets the progress value in the status file to 0.

    This function reads the status data from the status file, modifies the 'progress'
    key to 0, and then writes the updated data back to the file. It ensures that only the
    'progress' key is modified, leaving other keys unchanged.

    Args:
        None

    Returns:
        None
    """
    # Update the 'progress' key without reading and modifying other keys
    with open(statusPath, 'r') as file:
        # Read the current data from the file
        status = json.load(file)
        
        # Modify the 'progress' key
        status['progress'] = 0  # New value for progress
        

    with open(statusPath, 'w', encoding='utf-8') as file:    
        # Write the updated content back to the file
        json.dump(status, file, indent=4)

        

def renameFile():
    """
    Renames and copies current plot JSON files to previous plot file locations.

    This function copies files from the current plot paths to the corresponding previous plot paths.
    It checks whether each source file exists before copying it to the destination.
    
    The function uses a list of file paths for the current and previous plot data and utilizes 
    `shutil.copy2` to ensure both the file contents and metadata (such as timestamps) are preserved.

    Args:
        None

    Returns:
        None
    """
    # Define the old and new paths (including the file name)
    plotJsonPathList = ['./data/currPlotResult.json','./data/currInfectionRate.json','./data/currPlotAgeGroup.json','./data/currStackBar.json','./data/currPlotCountConnections.json',
                        './data/prevPlotResult.json','./data/prevInfectionRate.json','data/prevPlotAgeGroup.json','./data/prevStackBar.json','./data/prevPlotCountConnections.json']
    
    # Check if the file exists before renaming
    if os.path.exists(plotJsonPathList[0]):
        shutil.copy2(plotJsonPathList[0], plotJsonPathList[5])
    if os.path.exists(plotJsonPathList[1]):
        shutil.copy2(plotJsonPathList[1], plotJsonPathList[6])
    if os.path.exists(plotJsonPathList[2]):
        shutil.copy2(plotJsonPathList[2], plotJsonPathList[7])
    if os.path.exists(plotJsonPathList[3]):
        shutil.copy2(plotJsonPathList[3], plotJsonPathList[8])
    if os.path.exists(plotJsonPathList[4]):
        shutil.copy2(plotJsonPathList[4], plotJsonPathList[9])    



@app.callback(
    [Output('input-age-1', 'value'),
     Output('input-age-2', 'value'),
     Output('input-age-3', 'value'),
     Output('input-age-4', 'value'),
     Output('input-age-5', 'value'),
     Output('input-age-6', 'value'),
     Output('input-age-7', 'value'),
     Output('input-age-8', 'value')],
    [Input('dropdown-1', 'value'),
     Input('slider-2', 'value')]
)
def update_output(country, year):
    """
    Update the age distribution values based on the selected country and year.

    This callback is triggered by changes in the 'dropdown-1' and 'slider-2' inputs.
    If a valid country is selected, the function generates the age proportions for the
    specified country and year. These proportions are then returned as values for the
    input fields for age groups 1 through 5. If no valid country is selected, default
    values of 20 for each age group are returned.

    Args:
        country (str): The selected country from the dropdown.
        year (int): The selected year from the slider.

    Returns:
        tuple: A tuple containing the age proportions for each of the 5 age groups.
               If no valid country is selected, it returns default values of (20, 20, 20, 20, 20).
    """
    if country != 'Country' and country is not None:
        proportion = generateProportion(country, year)
        return proportion[0], proportion[1], proportion[2], proportion[3], proportion[4], proportion[5], proportion[6], proportion[7]
    else:
        return 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5



@app.callback(
    [Output('total-output', 'children')],
    [Input('input-age-1', 'value'),
     Input('input-age-2', 'value'),
     Input('input-age-3', 'value'),
     Input('input-age-4', 'value'),
     Input('input-age-5', 'value'),
     Input('input-age-6', 'value'),
     Input('input-age-7', 'value'),
     Input('input-age-8', 'value')],
)
def validate_inputs(age1, age2, age3, age4, age5, age6, age7, age8):
    """
    Validate the sum of the age group proportions and provide feedback.

    This callback is triggered by changes in the values of the five age input fields.
    It calculates the total sum of the age group proportions. If the sum is 100, the
    feedback is displayed in green, indicating that the input is valid. If the sum is not
    100, the feedback is displayed in red with a message indicating the error.

    Args:
        age1 (float): The proportion for the first age group.
        age2 (float): The proportion for the second age group.
        age3 (float): The proportion for the third age group.
        age4 (float): The proportion for the fourth age group.
        age5 (float): The proportion for the fifth age group.
        age6 (float): The proportion for the sixth age group.
        age7 (float): The proportion for the seventh age group.
        age8 (float): The proportion for the eigth age group.

    Returns:
        tuple: A tuple containing an HTML `Span` element that displays the total sum and
               a validation message. The feedback message is displayed in green if valid
               or red if the total does not sum to 100%.
    """
    # Handle None values (initial state)
    age1 = float(age1) if age1 is not None else 0
    age2 = float(age2) if age2 is not None else 0
    age3 = float(age3) if age3 is not None else 0
    age4 = float(age4) if age4 is not None else 0
    age5 = float(age5) if age5 is not None else 0
    age6 = float(age6) if age6 is not None else 0
    age7 = float(age7) if age7 is not None else 0
    age8 = float(age8) if age8 is not None else 0

    total = age1 + age2 + age3 + age4 + age5 + age6 + age7 + age8
    feedback = f"Total: {total}%"
    if total != 100:
        feedback += " (Invalid! Sum to 100%)"
        color = "red"
    else:
        color = "green"
    
    return (
        html.Span(feedback, style={"color": color}),
    )



@app.callback(
    Output('tbl_out', 'children'),
    [Input('tbl', 'active_cell'),
     Input('tbl', 'data')]  # Add input for table data
)
def update_table1(active_cell, table_data):
    """
    Update the output based on the active cell selection in the table.

    This callback listens for changes in the active cell selection within the table (`tbl`)
    and updates the output based on the selected cell. The output displays the value from 
    the selected cell, along with additional information such as the corresponding age group.
    If the selected column is related to infection rate reduction, it modifies the column
    header to reflect the full description. If the 'Age Group' column is selected, it displays
    only the value for that specific column.

    Args:
        active_cell (dict): Information about the currently active cell in the table, 
                             including row, column, and column_id.
        table_data (list): The data in the table, structured as a list of dictionaries 
                           where each dictionary represents a row.

    Returns:
        str: A string containing the age group and column data for the selected cell, 
             or a prompt message if no cell is selected.
    """
    # If a cell is selected
    if active_cell:
        row = active_cell['row']
        column_id = active_cell['column_id']
        
        # Retrieve the value from the table data using the row and column id
        value = table_data[row][column_id]
        if column_id != 'Age Group':
            ageGroupVal = table_data[row]['Age Group']
            if column_id == '1-14 days after first dose (95% CI)' or column_id == '15-28 days after first dose (95% CI)':
                column_id = 'Infection Rate Reduction ' + column_id
            return f'Age Group: {ageGroupVal}, {column_id}: {value}'
        
        return f'{column_id}: {value}'
    return "Click the table"


@app.callback(
    Output('contact-matrix-table-out', 'children'),
    [Input('contact-matrix-table', 'active_cell'),
     Input('contact-matrix-table', 'data')]  # Add input for table data
)
def update_table2(active_cell, table_data):
    """
    Update the output with information about the selected cell in the contact matrix table.

    This callback listens for a selection in the 'contact-matrix-table'. When a cell is clicked, it retrieves the 
    corresponding value from the table data and displays it along with the row and column identifiers. Specifically, 
    it shows the contact weight of connection between two age groups (represented by row and column IDs).

    Args:
        active_cell (dict): A dictionary containing the row and column indices of the currently selected cell in the table.
        table_data (list): A list of dictionaries representing the data of the table, where each dictionary corresponds to a row.

    Returns:
        str: A string displaying the contact weight of connection between the two age groups (row and column), or a default message 
             if no cell is selected.
    """
    # If a cell is selected
    if active_cell:

        row = active_cell['row']
        column_id = active_cell['column_id']
        row_id = table_data[row]['Age Group']
        # Retrieve the value from the table data using the row and column id
        value = table_data[row][column_id]
        return f'Contact weight of connection from {row_id} to {column_id} : {value}'
    return "Click the table"


# Callback to control the modal visibility and update button clicks
@app.callback(
    [Output('modal', 'style'),
     Output('open-modal-btn', 'n_clicks'),
     Output('close-modal-btn', 'n_clicks')],
    [Input('open-modal-btn', 'n_clicks'), 
     Input('close-modal-btn', 'n_clicks')],
    [dash.dependencies.State('modal', 'style')]
)
def toggle_modal(open_clicks, close_clicks, current_style):
    """
    Toggle the visibility of a modal when the open and close buttons are clicked.

    This callback listens for clicks on the 'open-modal-btn' and 'close-modal-btn'
    to control the visibility of the modal and update the click count of the buttons. 
    The modal is shown when the open button is clicked and hidden when the close button is clicked. 
    The click counts of both buttons are reset accordingly after each action.

    Args:
        open_clicks (int): The number of times the 'open-modal-btn' has been clicked.
        close_clicks (int): The number of times the 'close-modal-btn' has been clicked.
        current_style (dict): The current style of the modal, including its display property.

    Returns:
        tuple: A tuple containing:
            - A dictionary representing the updated style of the modal, including the display property ('flex' for visible, 'none' for hidden).
            - The updated click count for the 'open-modal-btn' (reset to 0 when clicked).
            - The updated click count for the 'close-modal-btn' (reset to 1 when clicked).
    """
    # Show the modal when open-modal-btn is clicked
    if open_clicks > 0 and close_clicks == 0:
        return {**current_style, 'display': 'flex'}, 0, 1  # Reset open button, set close button to 1

    # Close the modal when close-modal-btn is clicked
    if close_clicks > 0:
        return {**current_style, 'display': 'none'}, 1, 0  # Reset close button, set open button to 1

    return current_style, 0, 0  # Default case when no button is clicked


if __name__ == '__main__':
    app.run_server(debug=False)
    #print("url: http://localhost:8080/")
