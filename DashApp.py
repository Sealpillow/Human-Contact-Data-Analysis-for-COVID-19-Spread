from dash import Dash, html, dcc, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import subprocess
import dash_cytoscape as cyto
import os
import json
import jsonpickle
import plotly.io as pio
import dash
import plotly.graph_objects as go
from waitress import serve
from countryProportion import generateProportion
from plotGraph import plotCountConnections,plotDistributionSubPlot
import pandas as pd


current_dir = os.path.dirname(os.path.abspath(__file__))
# template_path = os.path.join(current_dir, "external_program.py")
template_path = os.path.join(current_dir, "SPAIR.py")
progress_path = os.path.join(current_dir, "progress.txt")
factors_path = os.path.join(current_dir, "./data/factors.csv")
# Create the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

df = pd.read_csv(factors_path)

dailyNetwork = None  # this hold the recently generated network
infectionGraph = None
populationPie = None
stackBarPlot = None
countPlot = None
distributionSubPlot = None
current_day = 1
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
                dcc.Input(id='seed-input', type='number', value=12345, className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Reproduction Number",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="The average number of people an infected person will spread a disease to")]),
                dcc.Input(id='overallReproNum-input', type='number', step=0.1, value=3.5, min = 1.0, max = 20, className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),  

                html.P([f"Population",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Size of population")]),
                dcc.Input(id='population-input', type='number', value=410, min = 50, placeholder='Enter population', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Days",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Number of simulation days")]),
                dcc.Input(id='day-input', type='number', value=100, min = 1, placeholder='Enter days', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),
                
                html.P([f"Infected population",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "5px"},title="Probability: 85% presymptomatic 15% asymptomatic")]),
                html.Div([
                dcc.Input(id='affected-input', type='number', value=5, min = 0, placeholder='Enter number of affected', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),

                html.P([f"Intervention Day",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="The day vaccination is implemented to population")]),
                dcc.Input(id='interventionDay-input', type='number', value=0, min = 0, placeholder='Enter Vaccination Intervention Day', className='dcc.Input',
                          style={'margin-bottom': '15px', 'width': '190px', 'height': '25px', 'font-size': '15px'}),          

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
                dcc.Dropdown(
                    sorted(['Singapore', 'Japan', 'United States','New Zealand','Australia']),
                    id='dropdown-1',
                    placeholder="Country",
                    searchable=False,optionHeight=20,
                    style={'margin-bottom': '10px', 'font-size': '15px', 'width': '190px'}    # Set the height
                ),
                dcc.Slider(
                    id='slider-2', min=1950, max=2023, step=1, 
                    value=2023, marks={1950: '1950', 2023: '2023'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div([
                    html.Label("Age Group (<25)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-1', type='number', min=0, step=1, value=10,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]), 
                
                html.Div([
                    html.Label("Age Group (25 - 44)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-2', type='number', min=0, step=1, value=15,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]), 
                
                html.Div([
                    html.Label("Age Group (45 - 64)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-3', type='number', min=0, step=1, value=25,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (65 - 74)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-4', type='number', min=0, step=1, value=25,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                html.Div([
                    html.Label("Age Group (>74)", style={'padding-right': '10px'}),
                    dcc.Input(id='input-age-5', type='number', min=0, step=1, value=25,
                               style={'margin-bottom': '15px', 'width': '50px', 'height': '25px', 'font-size': '15px'}),
                    html.Label('%'),  # Add % symbol beside input
                ]),
                
                html.P(id='total-output', style={'color': 'red'}),
                dcc.RadioItems(
                    id='connection-radio',
                    options=[
                        {'label': ' Same Daily Network', 'value': 'same'},
                        {'label': ' Unique Daily Network', 'value': 'unique'},
                        {'label': ' Complete Daily Network', 'value': 'complete'},
                        {'label': ' Model Network', 'value': 'model'},
                    ],
                    value='same',
                    style={'margin-bottom': '15px', 'color': 'white'}
                ),

                html.Div(id='output-div', style={'margin-top': '15px', 'color': 'white'}),

                html.P("*Only applies when re-generated"),
                dcc.Checklist(id='checkbox-list',
                              options=[{'label': ' Remove Non-Selected Node Connections', 'value': 'removeOthers'},
                                       {'label': ' Isolate Node in Infected state*', 'value': 'isolate'},
                                       {'label': ' Include Age factor*', 'value': 'age'},
                                       {'label': ' Include Vaccination factor*', 'value': 'vaccination'}],
                              value=[],
                              labelStyle={'margin-right': '10px'},
                              style={'color': 'white', 'margin-bottom': '15px'}),

                dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
                dbc.Progress(id="progress", value=0, label="", color="success",style={'margin-bottom': '5vh','--bs-progress-bar-color': 'black','--bs-progress-font-size': '0.9rem'}),
                html.P("Notes:",style={'margin-bottom': '1vh'}),
                html.P("Reproduction Number: 3.5"),
                html.P("Nodes having < 5 connections will have inner connections",style={'margin-bottom': '5vh'}),
            ], style={'display': 'flex', 'flex-direction': 'column', 'padding': '20px', 
                      'background-color': '#222', 'border-radius': '10px'}),

            # Second part: Node click data and status section
            html.Div([
                html.P([f"Node ID",html.I(className="bi bi-info-circle", style={"color": '#007BFF', "margin-left": "10px"},title="To observe selected individual connections by id")]),
                html.Div([
                dcc.Input(id='node-input', type='number', value=1,
                          style={'margin-bottom': '15px', 'width': '90px', 'height': '25px', 'font-size': '15px'}),
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

        ], className="left-panel", style={'flex': '1', 'padding': '20px'}),

        # Right panel
        html.Div([
            # First Cytoscape Network
            html.H3("Visualizing Network progression", style={'margin-top': '15px', 'margin-bottom': '15px', 'color': 'white'}),
            html.P(id='animation-day', children='Current Day: {current_day}',
                   style={'margin-top': '15px', 'margin-bottom': '15px', 'color': 'white', 'font-size': '15px'}),

            cyto.Cytoscape(
                id='animated-network',
                elements=[],
                layout={'name': 'concentric', 'animate': True, 'minNodeSpacing': 30, 'avoidOverlap': True},
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
                dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], 
                id='tbl',
                style_data_conditional=[
                    {
                        'if': {'state': 'active'},  # Apply styles when a cell is hovered
                        'backgroundColor': 'lightblue',  # Set hover background color
                        'color': 'black',  # Set hover text color
                        'border': '2px solid lightblue'
                    }
                ]),
                dbc.Alert(id='tbl_out'),
                dbc.Alert(
                    children=[
                        "Reference:",
                        html.Br(),
                        "- Age Group distribution: ", 
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
                    ],

                    id='tbl_references',
                    color="info"
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
    [Output('node-input', 'min'),
     Output('node-input', 'max')],
    Input('population-input', 'value')
)
def update_slider_based_on_days(population):
    if population is None:
        return 1, 1
    try:
        population = int(population)
        return 1, population

    except (ValueError, TypeError):
        # Default values if there's an error in input
        return 1, 1
    

@app.callback(
    Output('slider-1', 'value'),
    Input('slider-input', 'value'),
    State('slider-1', 'max')
)
def update_slider_value(input_value, max_value):
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
    return slider_value



def process_network(network,selected_node, checkbox): # this update the nodes in the cytoscape by using the give network
        statusMap = {
            'S': 'Susceptible',
            'P': 'Presymptomatic',
            'A': 'Asymptomatic',
            'I': 'Infected',
            'R': 'Recovered',
        }
        elements = []
        nodes = network.getNodes()
        sorted_keys = sorted(nodes.keys(), key=lambda k: int(k))  # Convert string keys to integers
        sorted_nodes_dict = {key: nodes[key] for key in sorted_keys}
        for node in sorted_nodes_dict.values():
            nodeConnections = node.getConnections()
            connections = sorted([str(nodeConnection) for nodeConnection in nodeConnections], key=int)
            connections_str = ', '.join(connections)
            # this is to generate the node {'data': {'id': '190', 'label': 'Node 190', 'status': 'Susceptible', 'age': '52', 'S': '1', 'P': '0', 'A': '0', 'I': '0', 'R': '0', 'day': 1, 'connections': '1'}}
            
            elements.append({'data': {'id': str(node.id), 
                             'label': f'Node {node.id}', 
                             'status': statusMap.get(node.status), 
                             'age': str(node.age),
                             'S': str(round(node.S* 100,1)) +'%', 
                             'P': str(round(node.P* 100,1)) +'%',
                             'A': str(round(node.A* 100,1)) +'%',
                             'I': str(round(node.I* 100,1)) +'%',
                             'R': str(round(node.R* 100,1)) +'%',
                             'day': node.day,
                             'connections':  connections_str}} #
                            )
                        
            # this produce the edge shown in the network {'data': {'source': '190', 'target': '1'}
            for connection in connections:
                elements.append({
                    'data': {
                        'source': str(node.id),
                        'target': str(connection)
                    }
                })
 
        # Filter based on selected node (optional)
        if selected_node is not None:
            if 'removeOthers' in checkbox: # Show selected nodes network
                nodeConnections = sorted_nodes_dict.get(str(selected_node)).getConnections()
                connections = [str(nodeConnection) for nodeConnection in nodeConnections]
                connections.append(str(selected_node))
                elements = [element for element in elements if 
                        ('id' in element['data'] and                # this is all the nodes info
                        element['data']['id'] in connections) or                 
                        ('source' in element['data'] and            # this is connections
                        (element['data']['source'] == str(selected_node) or 
                        element['data']['target'] == str(selected_node)))
                        ]  
            else:  # Show all nodes
                elements = [element for element in elements if               
                        ('source' not in element['data'] or            # this is all the nodes info
                        (element['data']['source'] == str(selected_node) or # this is connections
                        element['data']['target'] == str(selected_node)))
                        ]       
        return elements


@app.callback(
    [Output('cytoscape', 'elements'), Output('generate-button', 'n_clicks')],
    [Input('generate-button', 'n_clicks'),
     Input('node-input', 'value'),
     Input('slider-1', 'value'),
     Input('checkbox-list', 'value')],
    [State('input-age-1', 'value'),
     State('input-age-2', 'value'),
     State('input-age-3', 'value'),
     State('input-age-4', 'value'),
     State('input-age-5', 'value'),
     State('seed-input', 'value'),
     State('overallReproNum-input', 'value'),
     State('population-input', 'value'),
     State('day-input', 'value'),
     State('affected-input', 'value'),
     State('interventionDay-input', 'value'),
     State('connection-radio', 'value')]
)
def generate_and_update_network(n_clicks, selected_node, slider_value, checkbox, age1, age2, age3, age4, age5, seed, overallReproNum, population, days, affected, interventionDay,  radio):
    global dailyNetwork, infectionGraph, populationPie, stackBarPlot, current_day
    # Handle "Generate" button click
    if n_clicks > 0 and population is not None:
        try:
            reset_file(progress_path)
            proportionList = [str(age1), str(age2), str(age3), str(age4), str(age5)]
            result = subprocess.run(
                ['python', template_path, str(seed), str(overallReproNum), str(population), str(days), str(affected), str(interventionDay), str(radio)] + proportionList + checkbox,
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout.strip()
            output_data = json.loads(output)
            encoded_network = output_data.get('dailyNetwork') 
            infectionGraph  = pio.from_json(output_data.get('infectionGraph'))
            populationPie = pio.from_json(output_data.get('populationPie'))
            stackBarPlot = pio.from_json(output_data.get('stackBarPlot'))
            
            dailyNetwork = jsonpickle.decode(encoded_network)  # set the global dailyNetwork to the recently generated network
            network = dailyNetwork.getNetworkByDay('1') # despite the key was int -> due to encode it became str
            current_day = 1
            if network is None:
                return f"Generate Network to Start"
            elements = process_network(network,selected_node, checkbox)
        except subprocess.CalledProcessError as e:
            return f"Error in external program: {e.stderr}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    # Handle slider adjustment
    # if a network has already been generated, retrieved the global variable dailynetwork, and get the specific day network
    elif dailyNetwork is not None:  
        network = dailyNetwork.getNetworkByDay(str(slider_value))
        if network is None:
            return f"Generate Network to Start"
        elements = process_network(network,selected_node, checkbox)

    else:
        elements = []

    return elements, 0  # return updated elements and reset generate button presses


def split_connections(connections_str, items_per_line=8):
    # Split the connections string into a list of items
    connections_list = connections_str.split(', ')
    
    # Create lines of connections
    lines = []
    for i in range(0, len(connections_list), items_per_line):
        line = ', '.join(connections_list[i:i + items_per_line])
        lines.append(line)
    
    # Return the list of lines
    return lines
     

@app.callback(
    Output('click-node-data', 'children'),
    Input('cytoscape', 'tapNodeData')
)
def display_click_data(data):
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'yellow',
        'Asymptomatic': 'purple',
        'Infected': 'red',
        'Recovered': 'green',
    }
    if data:
        connections_str = data['connections']
        connection_lines = split_connections(connections_str)
       
        # Build the HTML Div output
        return html.Div([
            html.P([html.I(className="bi bi-calendar pe-1", style={"color": 'white', "margin-right": "5px"}), 
                    f"Day: {data['day']}"]),
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": 'white', "margin-right": "5px"}), 
                    f"Node: {data['label'][4:]}"]),
            html.P([html.I(className="bi bi-file-person-fill pe-1", style={"color": 'white', "margin-right": "5px"}), 
                    f"Age: {data['age']}"]),    
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get(data['status']), "margin-right": "5px"}), 
                    f"Status: {data['status']}"]),
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Susceptible'), "margin-right": "5px"}), 
                    f"Probabilty to Susceptible State: {data['S']}"]), 
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Presymptomatic'), "margin-right": "5px"}), 
                    f"Probabilty to Presymptomatic State: {data['P']}"]),
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Asymptomatic'), "margin-right": "5px"}), 
                    f"Probabilty to Asymptomatic State: {data['A']}"]),
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Infected'), "margin-right": "5px"}), 
                    f"Probabilty to Infected State: {data['I']}"]),
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Recovered'), "margin-right": "5px"}), 
                    f"Probabilty to Recovered State: {data['R']}"]),
            *[html.P(f"Connections: {line}", style={'word-wrap': 'break-word'}) if i == 0 else html.P(f"{line}", style={'word-wrap': 'break-word'}) 
              for i, line in enumerate(connection_lines)]
        ], style={'max-width': '100vh', 'font-size': '14px', 'margin-bottom': '15px'})

    return "Click a node in Network Exploration for details"





@app.callback(
    Output('status-data', 'children'),
    [Input('cytoscape', 'elements')],
    [State('slider-input', 'value')]

)
def display_nodes_status(elements, day):
    global countPlot
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'yellow',
        'Asymptomatic': 'purple',
        'Infected': 'red',
        'Recovered': 'green',
    }   
    if elements:
        # Retrieve status from the data dictionary
        # status = data.get('status', 'Status not available')
        sList = []
        pList = []
        aList = []
        iList = []
        rList = []
        totalConnections = 0
        count = 0
        # list of number of connections of nodes
        nodeConnectionsCount = []
        for element in elements:
            # {'data': {'id': '190', 'label': 'Node 190', 'status': 'Susceptible', 'age': '52', 'S': '1', 'P': '0', 'A': '0', 'I': '0', 'R': '0', 'day': 1, 'connections': '1'}}
            if 'status' in element['data']:              # this is all the nodes info
                if element['data']['status'] == 'Susceptible':
                    sList.append(element['data']['id'])
                elif element['data']['status'] == 'Presymptomatic':
                    pList.append(element['data']['id'])
                elif element['data']['status'] == 'Asymptomatic':
                    aList.append(element['data']['id'])
                elif element['data']['status'] == 'Infected':
                    iList.append(element['data']['id'])   
                else:
                    rList.append(element['data']['id'])  
                # number of connections a node have    
                nodeConnectionsNum = len(element['data']['connections'].split(', ')) 
                nodeConnectionsCount.append(nodeConnectionsNum)   
                totalConnections += nodeConnectionsNum
                count += 1
        countPlot = plotCountConnections(nodeConnectionsCount)    
        avgConnections = round(totalConnections/count,2)    
        sList_lines = split_connections(', '.join(sList))
        pList_lines = split_connections(', '.join(pList))
        aList_lines = split_connections(', '.join(aList))
        iList_lines = split_connections(', '.join(iList))
        rList_lines = split_connections(', '.join(rList))
         
        # Build the HTML Div outputbi 
        return html.Div([
            html.P([html.I(className="bi bi-people-fill pe-1", style={"color": "white", "margin-right": "5px"}),
                f"Overall Population status for Day: {day}"]),
            html.P([html.I(className="bi bi-link pe-1", style={"color": "white", "margin-right": "5px"}),
                f"Average Connections: {avgConnections}"]),  
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Susceptible'), "margin-right": "5px"}),
                f"Status: Susceptible"]), 
            *[html.P(f"Nodes: {line}") if i ==0 else html.P(f"{line}")  for i, line in enumerate(sList_lines)],
             html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Presymptomatic'), "margin-right": "5px"}),
                f"Status: Presymptomatic"]),
            *[html.P(f"Nodes: {line}") if i ==0 else html.P(f"{line}")  for i, line in enumerate(pList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Asymptomatic'), "margin-right": "5px"}),
                f"Status: Asymptomatic"]),
            *[html.P(f"Nodes: {line}") if i ==0 else html.P(f"{line}")  for i, line in enumerate(aList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Infected'), "margin-right": "5px"}),
                f"Status: Infected"]),
            *[html.P(f"Nodes: {line}") if i ==0 else html.P(f"{line}")  for i, line in enumerate(iList_lines)],
            html.P([html.I(className="bi bi-circle-fill pe-1", style={"color": statusColourMap.get('Recovered'), "margin-right": "5px"}),
                f"Status: Recovered"]),
            *[html.P(f"Nodes: {line}") if i ==0 else html.P(f"{line}")  for i, line in enumerate(rList_lines)]
        ])

    return "Generate network to see nodes status"
            
                     
@app.callback(
    Output('cytoscape', 'stylesheet'),
    Input('cytoscape', 'elements')
)
def update_stylesheet(elements):
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'yellow',
        'Asymptomatic': 'purple',
        'Infected': 'red',
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
            'curve-style': 'straight',
            'width': 2
        }
    })

    return stylesheet


@app.callback(Output('animated-network', 'elements'),
          [Input('interval-component', 'n_intervals'),
           Input('cytoscape', 'elements'),
           Input('checkbox-list', 'value'),
           Input('node-input', 'value')])
def animate_network(n, elements, checkbox, selected_node):
    
    global dailyNetwork, current_day
    if dailyNetwork is None:
       return [{'data': {'id': 'Error', 'label': f"Generate Network to Start"}}]
    else:
        network = dailyNetwork.getNetworkByDay(str(current_day)) 
        if network is None:
            return [{'data': {'id': 'Error', 'label': f"Generate Network to Start"}}]
        
        elements = process_network(network, selected_node, checkbox)
        
        # Increment the current day for the next interval
        current_day += 1
        if current_day > len(dailyNetwork.networks):  # Reset after reaching the last day
            current_day = 1
        
    return elements

@app.callback(
    Output('animated-network', 'stylesheet'),
    Input('animated-network', 'elements')
)
def update_stylesheet2(elements):
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'yellow',
        'Asymptomatic': 'purple',
        'Infected': 'red',
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
    Output('animation-day', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_population(n):
    global current_day
    return f"Current Day: {current_day}"


@app.callback(
    Output('plotly-graph1', 'figure'),
    [Input('cytoscape', 'elements'),
     Input('slider-input', 'value')]
)
def update_graph(elements, slider_value):
    # Example figure - replace with your actual data processing and plotting logic
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
        fig = go.Figure(infectionGraph) # make a copy of figure, without affecting it
        
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
    # Example figure - replace with your actual data processing and plotting logic
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
    Output('plotly-graph3', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    # Example figure - replace with your actual data processing and plotting logic
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
    Output('plotly-graph4', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    # Example figure - replace with your actual data processing and plotting logic
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
    Output('plotly-graph5', 'figure'),
    [Input('cytoscape', 'elements')]
)
def update_graph(elements):
    # Example figure - replace with your actual data processing and plotting logic
    global distributionSubPlot
    if distributionSubPlot is None:
        return plotDistributionSubPlot()
    else:
        return distributionSubPlot
                   
@app.callback(
    Output('cytoscape', 'layout'),
    [Input('reset-button', 'n_clicks')]
)
def reset_view(n_clicks):
    if n_clicks > 0:
        return {
            'name': 'concentric',  # Example layout to reset the view
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
    try:
        with open("progress.txt", "r") as f:
            progress = int(f.read().strip())
            progress = min(progress, 100)  # Ensure progress does not exceed 100%
    except (FileNotFoundError, ValueError):
        progress = 0

    # Determine the color based on the progress value
    if progress < 30:
        color = "danger"  # Red for low progress
    elif progress < 70:
        color = "warning"  # Yellow for medium progress
    else:
        color = "success"  # Green for high progress

    return progress, f"{progress} %" if progress >= 5 else "", color

def reset_file(file_path):
    with open(file_path, 'w') as f:
        f.write("0")  # Reset progress to 0


@app.callback(
    [Output('input-age-1', 'value'),
     Output('input-age-2', 'value'),
     Output('input-age-3', 'value'),
     Output('input-age-4', 'value'),
     Output('input-age-5', 'value')],
    [Input('dropdown-1', 'value'),
     Input('slider-2', 'value')]
)
def update_output(country, year):
    if country != 'Country' and country is not None:
        proportion = generateProportion(country, year)
        return proportion[0],proportion[1],proportion[2],proportion[3],proportion[4]
    else:
        return 20,20,20,20,20


@app.callback(
    [Output('total-output', 'children')],
    [Input('input-age-1', 'value'),
     Input('input-age-2', 'value'),
     Input('input-age-3', 'value'),
     Input('input-age-4', 'value'),
     Input('input-age-5', 'value')],
)
def validate_inputs(age1, age2, age3, age4, age5):
    # Handle None values (initial state)
    age1 = int(age1) if age1 is not None else 0
    age2 = int(age2) if age2 is not None else 0
    age3 = int(age3) if age3 is not None else 0
    age4 = int(age4) if age4 is not None else 0
    age5 = int(age5) if age5 is not None else 0

    total = age1 + age2 + age3 + age4 + age5
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
def update_table(active_cell, table_data):
    if active_cell:
        row = active_cell['row']
        #column = active_cell['column']
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


if __name__ == '__main__':
    #app.run_server(debug=False)

    #print("url: http://localhost:8080/")

    serve(app.server, host='0.0.0.0', port=8080, threads=7)

