import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import scipy.stats as stats 
from scipy.stats import lognorm, norm
from plotly.subplots import make_subplots
import os
import pandas as pd
import plotly.graph_objects as go
from collections import Counter, defaultdict
current_dir = os.path.dirname(os.path.abspath(__file__))

def plotResult(days,susceptible_counts,presymptomatic_counts,asymptomatic_counts,infected_counts,recovered_counts):
    """
    Generates a multi-line plot to visualize the progression of population health states 
    over a specified number of days using Plotly.

    Parameters:
        days (int): Total number of days in the simulation.
        susceptible_counts (list): Daily counts of individuals in the 'Susceptible' state.
        presymptomatic_counts (list): Daily counts of individuals in the 'Presymptomatic' state.
        asymptomatic_counts (list): Daily counts of individuals in the 'Asymptomatic' state.
        infected_counts (list): Daily counts of individuals in the 'Infected' state.
        recovered_counts (list): Daily counts of individuals in the 'Recovered' state.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure displaying the multi-line plot for all states.

    Description:
        - Maps each health state to a unique color using `statusColourMap`.
        - Creates a separate line trace for each health state, plotting its daily counts over time.
        - Combines all traces into a single Plotly figure.
        - The x-axis represents days, while the y-axis represents the population in each state.
        - Includes legends and axis labels for clarity.
    """


    # plotly
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }   
    data = {
        'Susceptible': susceptible_counts,
        'Presymptomatic': presymptomatic_counts,
        'Asymptomatic': asymptomatic_counts,
        'Infectious': infected_counts,
        'Recovered': recovered_counts
    }

    # Define the order for the plot (e.g., you want 'Infectious' to be plotted last)
    ordered_labels = ['Susceptible','Recovered', 'Infectious','Asymptomatic','Presymptomatic']  # Custom order

    # Create a list of traces in the desired order
    traces = []
    for label in ordered_labels:
        counts = data[label]
        trace = go.Scatter(
            x=list(range(1, days + 1)),
            y=counts,
            mode='lines+text',
            name=label,
            line=dict(color=statusColourMap.get(label, 'black'))
        )
        traces.append(trace)

    # Combine traces into a figure
    fig = go.Figure(data=traces)

    # Add labels and title
    fig.update_layout(
        xaxis=dict(range=[1, days+1], dtick=10),
        xaxis_title='Days',
        yaxis_title='Population',
        legend_title='Legend',
        title_text="SPAIR Model Prediction",
        font=dict(size=16)
    )
    fig.write_json('./data/currPlotResult.json')
    # Show the figure
    #fig.show()
    return fig   


def plotInfectionRate(days, susceptible_counts):
    # plotly color map for susceptible decrease rate
    statusColourMap = {
        'Infection Rate': 'darkred',
    }

    # Calculate the rate of decrease in susceptible counts
    susceptible_decrease_rate = [0] + [susceptible_counts[i - 1] - susceptible_counts[i] for i in range(1, len(susceptible_counts))]  # Decrease in susceptible population
    susceptible_decrease_rate_per_susceptible = [round(rate / susceptible_counts[i - 1]*100,2) if susceptible_counts[i - 1] > 0 else 0 for i, rate in enumerate(susceptible_decrease_rate)][1:]  # Avoid division by 0 and skip first day
    #overallInfectionRate = round(sum(susceptible_decrease_rate_per_susceptible)/len(susceptible_decrease_rate_per_susceptible),2)
    overallInfectionRate = round((susceptible_counts[0]-susceptible_counts[-1])/susceptible_counts[0]*100,2)
    # Find the peak of susceptible decrease rate
    peak_day = susceptible_decrease_rate_per_susceptible.index(max(susceptible_decrease_rate_per_susceptible)) + 2  # +2 to adjust for starting from day 2
    peak_value = max(susceptible_decrease_rate_per_susceptible)

    # Create the plot for susceptible decrease rate
    susceptible_decrease_trace = go.Scatter(
        x=list(range(2, days + 1)),  # Start from day 2 since first day doesn't have a decrease
        y=susceptible_decrease_rate_per_susceptible,
        mode='lines+text',
        name="Infection Rate",
        line=dict(color=statusColourMap.get('Infection Rate', 'blue'))  # Dashed line for decrease rate
    )

    # Create a marker for the peak
    peak_marker = go.Scatter(
        x=[peak_day],
        y=[peak_value],
        mode='markers+text',
        name="Peak",
        marker=dict(color='red', size=10, symbol='star'),
        text=[f'Day {peak_day}: {peak_value:.2f}%'],
        #textposition='top center'
        textposition='middle right'
    )

    # Combine both the susceptible decrease rate and the peak marker
    fig = go.Figure(data=[susceptible_decrease_trace, peak_marker])

    # Add labels and title
    fig.update_layout(
        xaxis=dict(range=[1, days+1], dtick=10),
        xaxis_title='Days',
        yaxis_title='Infection Rate',
        legend_title='Legend',
        title_text=f"Infection Rate (Overall Infection Rate: {overallInfectionRate}%)",
        font=dict(size=16)
    )
    fig.write_json('./data/currInfectionRate.json')
    # Show the figure
    #fig.show()
    return fig, overallInfectionRate, susceptible_decrease_rate_per_susceptible



def plotAgeGroup(inputPopulation, specificProportion):
    """
    Generates a pie chart to visualize the distribution of population across age groups.

    Parameters:
        inputPopulation (int): Total population size.
        specificProportion (list): Percentage distribution of population across age groups 
                                   in the following order: 
                                   ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '>70'].

    Returns:
        tuple: A Plotly pie chart figure and the adjusted population distribution across 
               age groups based on the input percentage distribution.

    Description:
        - Calculates the population for each age group based on the input percentages.
        - Adjusts the calculated values to ensure the sum matches the input population.
        - Creates a dual-layer pie chart:
          - The outer layer displays age group labels.
          - The inner layer displays the percentage composition.
        - Uses a custom color palette for the pie chart.
        - The chart does not include a legend and is titled "Age Group Composition."
    """

    # inputPopuulation = 410

    # specificProportion = [28, 35, 24, 8, 5] percentage of each age group
    data = {
    '0-9':  round(inputPopulation*specificProportion[0]/100),
    '10-19':  round(inputPopulation*specificProportion[1]/100),
    '20-29':  round(inputPopulation*specificProportion[2]/100),
    '30-39':  round(inputPopulation*specificProportion[3]/100),
    '40-49': round(inputPopulation*specificProportion[4]/100),
    '50-59': round(inputPopulation*specificProportion[5]/100),
    '60-69': round(inputPopulation*specificProportion[6]/100),
    '>70': round(inputPopulation*specificProportion[7]/100),
    }
    ageGroupsDistribution = [v for v in data.values()]
    while(sum(ageGroupsDistribution)>inputPopulation): 
        ageGroupsDistribution[ageGroupsDistribution.index(max(ageGroupsDistribution))]-=1
    while(sum(ageGroupsDistribution)<inputPopulation): 
        ageGroupsDistribution[ageGroupsDistribution.index(min(ageGroupsDistribution))]+=1    
    # Create the bar graph
    categories = list(data.keys())
    values = list(data.values())
    # Define common properties for both traces
    common_props = dict(
        labels=categories,
        values=values,
        marker=dict(colors=['#e60049','#FFA500', '#FFD700','#32CD32','#0bb4ff','#FFC0CB','#00cfad','#A020F0'])  # Custom color sequence
    )

    # First trace: showing percentage outside
    trace1 = go.Pie(
        **common_props,
        textinfo='label',
        textposition='outside',
        textfont=dict(size=14, color="black"),
        sort = False
    )

    # Second trace: showing category labels inside
    trace2 = go.Pie(
        **common_props,
        textinfo='percent + value',
        textposition='inside',
        textfont=dict(size=14, color="black"),
        sort = False
    )

    # Create the figure with both traces overlapping
    fig = go.Figure(data=[trace1, trace2],)

    # Remove the legend
    fig.update_layout(showlegend=False, 
                      title_text= "Overall Population Age Group Composition",
                      font=dict(size=16))
    fig.write_json('./data/currPlotAgeGroup.json')
    # Show the pie chart
    #fig.show()
    
    return fig, ageGroupsDistribution


def plotStackBar(days,susceptible_counts,presymptomatic_counts,asymptomatic_counts,infected_counts,recovered_counts):
    """
    Generates a stacked bar plot to visualize the distribution of infection states over a specified number of days.

    Parameters:
        days (int): Total number of days in the simulation.
        susceptible_counts (list): Daily counts of individuals in the 'Susceptible' state.
        presymptomatic_counts (list): Daily counts of individuals in the 'Presymptomatic' state.
        asymptomatic_counts (list): Daily counts of individuals in the 'Asymptomatic' state.
        infected_counts (list): Daily counts of individuals in the 'Infected' state.
        recovered_counts (list): Daily counts of individuals in the 'Recovered' state.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure displaying a stacked bar plot for all infection states.

    Description:
        - Creates a stacked bar chart where each bar represents the total count for a specific day.
        - Each section of the bar corresponds to a different infection state (Susceptible, Presymptomatic, Asymptomatic, Infected, Recovered).
        - Uses a color mapping for each infection state to visually distinguish between them.
        - The x-axis represents the days, and the y-axis represents the counts of individuals in each infection state.
        - The chart is titled "Stacked Bar Plot of Infection States Over Days" with appropriate axis and legend titles.
    """

    # plotly
    statusColourMap = {
        'Susceptible': 'blue',
        'Presymptomatic': 'gold',
        'Asymptomatic': 'purple',
        'Infectious': 'red',
        'Recovered': 'green',
    }   
    # Create the data dictionary
    data = {
        'Susceptible': susceptible_counts,
        'Presymptomatic': presymptomatic_counts,
        'Asymptomatic': asymptomatic_counts,
        'Infectious': infected_counts,
        'Recovered': recovered_counts
    }

    # Create a stacked bar plot
    fig = go.Figure()

    # Add traces for each category with color mapping
    for label, counts in data.items():
        fig.add_trace(go.Bar(
            x=list(range(1, days + 1)),  # X-axis labels as days
            y=counts,
            name=label,
            marker_color=statusColourMap[label],  # Use the color mapping
        ))

    # Update layout for stacked bar
    fig.update_layout(
        title='Stacked Bar Plot of Infection States Over Days',
        barmode='stack',
        xaxis_title='Days',
        yaxis_title='Counts',
        legend_title='Infection States',
        font=dict(size=16)
    )
    fig.write_json('./data/currStackBar.json')
    # Show the plot
    #fig.show()
    return fig

def plotCountConnections(connections):
    """
    Generates a bar plot to visualize the frequency distribution of connections.

    Parameters:
        connections (list): A list of integers representing the number of connections for each individual.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure displaying a count plot of the frequency distribution of connections.

    Description:
        - Creates a bar chart where the x-axis represents the number of connections and the y-axis represents 
          the frequency (count) of individuals having that number of connections.
        - The data is grouped by the number of connections, and the count of each unique value is computed.
        - The chart includes a title "Count Plot of Connections" and appropriate axis labels.
        - The x-axis is customized to ensure that all possible values of connections are displayed.
    """

    # Example data with integers
    data = {
        'Connections': connections
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Count the frequency of each unique value
    counts = df['Connections'].value_counts().sort_index()

    # Create the count plot using go.Bar
    fig = go.Figure(data=[go.Bar(x=counts.index, y=counts.values)])

    # Update the layout to add titles
    fig.update_layout(
        title="Count Plot of Connections",
        xaxis_title="Connections",
        yaxis_title="Count",
        font=dict(size=16),
    )
    x_range = list(range(min(connections), max(connections)+1))
    # Ensure all x-axis labels are displayed
    fig.update_xaxes(tickmode='array', tickvals=x_range)
    # Show the plot
    #fig.show()
    fig.write_json('./data/currPlotCountConnections.json')
    return fig

def plotIndiConnAgeGroup(data, id):

    # Define custom bins
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, np.inf]

    # Use np.histogram to calculate the frequency of each bin
    hist_values, bin_edges = np.histogram(data, bins=bins)

    # Create the bar graph
    categories = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    values = hist_values

    # Calculate percentages for text
    total = sum(values)
    percentages = [(value / total) * 100 for value in values]

    # Define common properties for both traces
    common_props = dict(
        labels=categories,
        values=values,
        marker=dict(colors=['#e60049','#FFA500', '#FFD700','#32CD32','#0bb4ff','#FFC0CB','#00cfad','#A020F0'])  # Custom color sequence
    )

    # First trace: showing percentage outside
    trace1 = go.Pie(
        **common_props,
        textinfo='label',
        textposition='outside',
        textfont=dict(size=14, color="black"),
        sort = False
    )

    # Second trace: showing category labels inside
    trace2 = go.Pie(
        **common_props,
        textinfo='percent + value',
        textposition='inside',
        textfont=dict(size=14, color="black"),
        sort = False
    )

    # Create the figure with both traces overlapping
    fig = go.Figure(data=[trace1, trace2],)

    # Remove the legend
    fig.update_layout(showlegend=False, 
                      title=f"Selected Individual Node {id} Connections Age Group",
                      font=dict(size=16))

    # Show the pie chart
    #fig.show()
    
    return fig



def plotDistributionSubPlot():
    """
    Creates a set of distribution plots showing the cumulative distribution function (CDF) for 
    different stages of infection: Presymptomatic, Infectious, and Asymptomatic.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure containing three subplots, each displaying a CDF 
        for a different stage of infection.

    Description:
        - The first subplot displays the CDF for the presymptomatic stage based on a lognormal distribution.
        - The second subplot displays the CDF for the symptomatic stage based on a normal distribution.
        - The third subplot displays the CDF for the asymptomatic stage based on a normal distribution.
        - Each subplot includes axes labeled with "Time" (x-axis) and "Probability" (y-axis), and is 
          designed to provide insights into the distribution of infection stages over time.
        - The overall figure is titled 'Distribution Plots: Presymptomatic, Infectious, Asymptomatic'.
    """

    # Mean and standard deviation for the lognormal distribution
    meanP = 1.43
    stdP = 0.66

    # X values for the distribution
    x = list(range(0, 51))

    # Calculate the cumulative distribution function (CDF)
    y1 = [lognorm(s=meanP, scale=np.exp(stdP)).cdf(v) for v in range(0, 51)]

    # Create a subplot with 1 row and 2 columns (you can modify the rows and columns as needed)
    fig = make_subplots(rows=1, cols=3, subplot_titles=["Presymptomatic", "Infectious", "Asymptomatic"])

    # Add the first plot (CDF) to the first subplot
    fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Presymptomatic'), row=1, col=1)

    # Mean and standard deviation for the normal distribution
    meanA = 20.0                                            # Mean
    stdA = 5.0                                              # Standard deviation

    # Add another plot (e.g., a normal distribution PDF) to the second subplot
    y2 = [norm(loc=meanA, scale=stdA).cdf(v) for v in range(0,51) ]
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Infectious'), row=1, col=2)


    # Mean and standard deviation for the normal distribution
    meanI = 8.8                                             # Mean
    stdI = 3.88                                             # Standard deviation

    # Add another plot (e.g., a normal distribution PDF) to the second subplot
    y3 = [norm(loc=meanI, scale=stdI).cdf(v) for v in range(0,51) ]
    fig.add_trace(go.Scatter(x=x, y=y3, mode='lines', name='Asymptomatic'), row=1, col=3)

    # Update the layout for the entire figure (for common settings like title, etc.)
    fig.update_layout(
        title='Distribution Plots: Presymptomatic, Infectious, Asymptomatic',
        showlegend=False,
        font=dict(size=16)
    )

    # Customize axes for individual subplots
    fig.update_xaxes(title_text='Time', row=1, col=1)
    fig.update_yaxes(title_text='Probability', row=1, col=1, range=[0, 1])
    fig.update_xaxes(title_text='Time', row=1, col=2)
    fig.update_yaxes(title_text='Probability', row=1, col=2, range=[0, 1])
    fig.update_xaxes(title_text='Time', row=1, col=3)
    fig.update_yaxes(title_text='Probability', row=1, col=3, range=[0, 1])

    # Show the plot
    #fig.show()
    return fig

def plotDegreeVsInfection(dailyNetwork, population, days):
    data = {
        "node_id": [person for person in range(1, population+1)],
        "connections": [-1 for person in range(1, population+1)],
        "infection_status": [None for person in range(1, population+1)],  # None means never infected
        "day_of_spread": ['-' for person in range(1, population+1)],
    }
    pool = []
    for person in range(1, population+1):
        sumConnections = 0
        infection = None
        for day in range(1, days+1):
            network = dailyNetwork.getNetworkByDay(day)
            currNode = network.getNode(person)
            status = currNode.status
            sumConnections+=len(currNode.connections)
            if (status == 'P' or status == 'A') and day != 1: # at the point where the person is infected
                node = prev
                # scatter point to indicate day of infection -> node_id: 1, connections: 1, infection_status: 2, day_of_spread: -
                data["connections"][person-1] = len(node.connections) # connection the person came into contact with
                data["infection_status"][person-1] = day # the day where person transition to a hiddenspreader
                
                # scatter point to indicate as hidden spreader -> node_id: 1, connections: 1, infection_status: A, day_of_spread: -
                data["node_id"].append(person)
                data["connections"].append(len(node.connections))
                data["infection_status"].append(status)
                data['day_of_spread'].append('-')

                count = 0
                # checking yesterday node connections if there only hidden spreaders(A/P) and non infected
                validStates = []
                for n in prev.connections: 
                    status = prevNetwork.getNode(n).status
                    if status != 'I': 
                        count+=1
                        if status != 'R':
                            validStates.append(n) # contain only S, A, P 
                if count == len(prev.connections): # if all node connections are only hidden spreaders(A/P) and non infected(S)
                    # embed day of spread
                    # pool = [(1,2),(2,2),(3,2)....] contains(A/P/S)
                    pool.extend([(p,day-1) for p in validStates])  # add it to the potential hidden spreader pool
                infection =  status
                break
            prev = currNode
            prevNetwork = network
        if infection == None:
            data["infection_status"][person-1] = 'S'
            data['connections'][person-1] = sumConnections / days

    # Create a dictionary to store the letter and corresponding values
    spreadHistory = defaultdict(list)

    # Loop through the list and store the values for each letter
    for person, day in pool:
        spreadHistory[person].append(day)
        spreadHistory[person].sort()
        
    # Create the desired output for letters that appear more than once
    potentialSpreaders = [(person, sorted(set(days))) for person, days in spreadHistory.items()]

    for spreader, daysList in potentialSpreaders:
        if spreader in data['node_id']:
            index = data['node_id'].index(spreader)
            connections = data['connections'][index]
            infection_status = 'H'
            # Append the new data to each list
            data['node_id'].append(spreader)
            data['connections'].append(connections)
            data['infection_status'].append(infection_status)
            data['day_of_spread'].append(','.join(map(str, daysList)))

    df = pd.DataFrame(data)

    hiddenSpreadersGroup = df[df['infection_status'].isin(['A', 'P'])]
    potentialHiddenSpreadersGroup = df[df['infection_status'] == 'H']

    # Create a list to hold the new rows
    new_rows = []
    # Loop through hidden spreaders group to check if they were correctly identified
    for _, row in hiddenSpreadersGroup.iterrows():
        node_id = row['node_id']
        connections = row['connections']
        
        # Check if the node_id is in the potential hidden spreaders group
        potential_match = potentialHiddenSpreadersGroup[potentialHiddenSpreadersGroup['node_id'] == node_id]
        
        if not potential_match.empty:
            day_of_spread = potential_match['day_of_spread'].values[0]
            # True Positive (TP): Correct prediction -> Actual hidden spreaders ('A', 'P') that are correctly predicted as potential hidden spreaders ('H').
            new_row = {'node_id': node_id, 'connections': connections, 'infection_status': 'O', 'day_of_spread': day_of_spread}
        else:
            # False Negative (FN): Missed prediction -> Actual hidden spreaders ('A', 'P') that are not predicted as hidden spreaders.
            new_row = {'node_id': node_id, 'connections': connections, 'infection_status': 'X', 'day_of_spread': '-'}
        # Append the new row to the list of new rows
        new_rows.append(new_row)

    # Create a DataFrame from the new rows
    new_df = pd.DataFrame(new_rows)

    # Concatenate the new rows to the original DataFrame
    df = pd.concat([df, new_df], ignore_index=True)

    # Map infection status to categories for visualization purposes
    y_levels = {
        'Remained Susceptible': days + 10,                   # High Y for "Remained S"
        'Hidden Spreader': days + 20,                        # Even higher Y for "Hidden Spreaders"
        'Potential Hidden Spreader': days + 30,              # Even higher Y for "Potential Hidden Spreader"
        'Missed Prediction Hidden Spreader': days + 40,      # Even higher Y for "Missed prediction Hidden Spreader"
        'Correct Prediction Hidden Spreader': days + 50      # Even higher Y for "Correct prediction Hidden Spreader"
    }

    # Apply fixed infection day based on infection status
    # Set y-axis positions for different categories in the graph
    df['infection_day_fixed'] = df['infection_status'].apply(
        lambda x: y_levels['Remained Susceptible'] if x == "S" else
        y_levels['Hidden Spreader'] if x in ('A', 'P') else
        y_levels['Potential Hidden Spreader'] if x == 'H' else
        y_levels['Missed Prediction Hidden Spreader'] if x == 'X' else
        y_levels['Correct Prediction Hidden Spreader'] if x == 'O' else x
    )

    # Classify the nodes into categories based on their infection status
    df['category'] = df['infection_status'].apply(
        lambda x: "Remained Susceptible" if x == "S" else
        "Hidden Spreader" if x in ('A', 'P') else
        "Potential Hidden Spreader" if x == 'H' else
        "Missed Prediction Hidden Spreader" if x == 'X' else
        "Correct Prediction Hidden Spreader" if x == 'O' else
        "Early Infection" if (isinstance(x, int) and x < 10) else "Late Infection"
    )

    # Create hover text based on infection status
    df["hover_text"] = df.apply(
        lambda row: f"Node {row['node_id']}, connections: {row['connections']}, Infection Day: {row['infection_day_fixed']}"    # scatter points of hidden spreaders day of infection
        if isinstance(row['infection_status'], int) else
        f"Node {row['node_id']}, Connections: {row['connections']}, Day(s) of spread: {row['day_of_spread']}"  # scatter points of hidden spreaders day of spread
        if row['infection_status'] == 'O' else
        f"Node {row['node_id']}, Connections: {row['connections']}, In Infectious Community: ✅" # scatter points of Missed hidden spreaders 
        if row['infection_status'] == 'X' else
        f"Node {row['node_id']}, Connections: {row['connections']}, Infection Status: {row['infection_status']}" ,
        axis=1
    )

    # Grouping by (connections, infection_day_fixed) and concatenating node info (sorted by node_id)
    point_info = defaultdict(list)
    for node_id, deg, day, text in zip(df['node_id'], df['connections'], df['infection_day_fixed'], df['hover_text']):
        point_info[(deg, day)].append((node_id, text))  # Store as tuple (node_id, text) for sorting

    # Sort by node_id and join with HTML line breaks
    df["grouped_hover_text"] = df.apply(
        lambda row: "<br>".join(text for _, text in sorted(point_info[(row['connections'], row['infection_day_fixed'])])),
        axis=1
    )

    # Scatter plot with go.Scatter
    fig = go.Figure()

    # Map the infection status to colors manually
    color_map = {
        "Correct Prediction Hidden Spreader":'green',
        "Missed Prediction Hidden Spreader": 'black',
        "Potential Hidden Spreader":'pink',
        "Hidden Spreader": 'purple',
        "Remained Susceptible": 'blue',
        "Late Infection": 'red',
        "Early Infection": 'orange',
    }
    # Add traces for each category
    for category, color in color_map.items():
        category_df = df[df['category'] == category]
        
        fig.add_trace(go.Scatter(
            x=category_df["connections"],
            y=category_df["infection_day_fixed"],
            mode='markers',
            marker=dict(color=color),
            text=category_df["grouped_hover_text"],  # Hover text
            hoverinfo="text",  # Show text on hover
            name=category  # Add the category to the legend
        ))

    # Update layout to include the legend
    fig.update_layout(
        title="Hidden Spreader Prediction",
        xaxis_title="Average Number of Connections",
        yaxis_title="Infection Day, Prediction and Result",
        yaxis=dict(
            tickvals=list(range(0, days + 60, 10)) + [val for val in y_levels.values()],
            ticktext=[str(i) for i in range(0, days + 10, 10)] + [key for key in y_levels.keys()]
        ),
        showlegend=True  # Enable legend display
    )

    truePositiveRateFig = computeConfusionMatrixFromDF(df)

    # Show the figure
    #fig.show()
    return fig, truePositiveRateFig





def computeConfusionMatrixFromDF(df):
    # Initialize confusion matrix counts
    TP = FN = 0

    # Compute confusion matrix for model evaluation (TP, FN)
    hidden_spreaders = df[df['infection_status'].isin(['A', 'P'])]
    potential_spreaders = df[df['infection_status'] == 'H']
    
    merged = hidden_spreaders.merge(
        potential_spreaders[['node_id']], 
        on='node_id', 
        how='left', 
        indicator=True
    )
    
    TP = (merged['_merge'] == 'both').sum()          # True Positives: Correctly Predicted Hidden Spreader
    FN = (merged['_merge'] == 'left_only').sum()     # False Negatives: Missed Hidden Spreader
    truePositiveRate = np.array([[TP], [FN]])  # Only one column: Predicted Hidden
    
    precision = round(TP / (TP + FN + 1e-6), 2)  # Prevent division by zero

    # Create confusion matrix plot
    fig = go.Figure(data=go.Heatmap(
        z=truePositiveRate,
        x=['Actual: Hidden'],
        y=['Prediction: Hidden', 'Prediction: Missed'],
        colorscale='Blues',
        text=truePositiveRate,
        texttemplate='%{text}',
        showscale=True
    ))
    
    fig.update_layout(
        title=f"True Positive Rate({precision:.2f})",
        font=dict(size=16, color="black")
        #width = 600,
        #height = 600
    )

    # Show the figure
    #fig.show()
    return fig
