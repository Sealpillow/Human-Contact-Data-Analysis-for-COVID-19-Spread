import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import scipy.stats as stats 
from scipy.stats import lognorm, norm
from plotly.subplots import make_subplots
import os
import pandas as pd
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
        'Presymptomatic': 'yellow',
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

    # Create a list of traces
    traces = []
    for label, counts in data.items():
        trace = go.Scatter(
            x=list(range(1, days + 1)), 
            y=counts, 
            mode='lines+text', 
            name=label,
            #text=counts,
            #textposition='top right',
            #textfont=dict(size=8),
            line=dict(color=statusColourMap.get(label, 'black'))
        )
        traces.append(trace)

    # Combine traces into a figure
    fig = go.Figure(data=traces)

    # Add labels and title
    fig.update_layout(
        xaxis=dict(range=[1, days+1],dtick = 10),
        xaxis_title='Days',
        yaxis_title='Population',
        legend_title='Legend',
        title_text= "SPAIR Model Prediction"
    )
    fig.write_json('./data/currPlotResult.json')
    # Show the figure
    #fig.show()
    return fig   

def plotAgeGroup(inputPopulation, specificProportion):
    """
    Generates a pie chart to visualize the distribution of population across age groups.

    Parameters:
        inputPopulation (int): Total population size.
        specificProportion (list): Percentage distribution of population across age groups 
                                   in the following order: 
                                   ['< 25', '25 - 44', '45 - 64', '65 - 74', '> 74'].

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
    '< 25':  round(inputPopulation*specificProportion[0]/100),
    '25 - 44':  round(inputPopulation*specificProportion[1]/100),
    '45 - 64':  round(inputPopulation*specificProportion[2]/100),
    '65 - 74':  round(inputPopulation*specificProportion[3]/100),
    '> 74': round(inputPopulation*specificProportion[4]/100),
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
        marker=dict(colors=['#e60049','#FFA500', '#FFD700','#32CD32','#0bb4ff'])  # Custom color sequence
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
    fig.update_layout(showlegend=False, title_text= "Overall Population Age Group Composition")
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
        'Presymptomatic': 'yellow',
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
        legend_title='Infection States'
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
        yaxis_title="Count"
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
        marker=dict(colors=['#e60049','#FFA500', '#FFD700','#32CD32','#0bb4ff'])  # Custom color sequence
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
    fig.update_layout(showlegend=False, title=f"Selected Individual Node {id} Connections Age Group",)

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
        showlegend=False
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