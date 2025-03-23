from dash import dash_table
import pandas as pd
import numpy as np
import os
currentDir = os.path.dirname(os.path.abspath(__file__))

def generateContactMatrixTable():
    """
    Generates a contact matrix table for age group interactions based on predefined contact data.

    This function constructs a contact matrix table from a predefined set of contact data, which represents the 
    frequency of interactions between individuals from different age groups. The contact data is displayed as is. 
    Each cell in the table shows the raw frequency of interactions between the corresponding age groups.

    The matrix is represented in a DataFrame with age groups as both rows and columns. Additionally, the table includes 
    hover effects for better interactivity.

    Returns:
    - dash_table.DataTable: A Dash table component displaying the raw contact matrix with age groups as rows and columns.
    """
    # Example contact matrix data
    MFull = np.array([
        [19.2, 4.8, 3.0, 7.1, 3.7, 3.1, 2.3, 1.4, 1.4],
        [4.8, 42.4, 6.4, 5.4, 7.5, 5.0, 1.8, 1.7, 1.7],
        [3.0, 6.4, 20.7, 9.2, 7.1, 6.3, 2.0, 0.9, 0.9],
        [7.1, 5.4, 9.2, 16.9, 10.1, 6.8, 3.4, 1.5, 1.5],
        [3.7, 7.5, 7.1, 10.1, 13.1, 7.4, 2.6, 2.1, 2.1],
        [3.1, 5.0, 6.3, 6.8, 7.4, 10.4, 3.5, 1.8, 1.8],
        [2.3, 1.8, 2.0, 3.4, 2.6, 3.5, 7.5, 3.2, 3.2],
        [1.4, 1.7, 0.9, 1.5, 2.1, 1.8, 3.2, 7.2, 7.2],
        [1.4, 1.7, 0.9, 1.5, 2.1, 1.8, 3.2, 7.2, 7.2]
    ])

    # Define the index labels
    indexLabels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

    # Create a DataFrame with the appropriate index
    df = pd.DataFrame(MFull, index=indexLabels, columns=indexLabels)

    # Convert the DataFrame values to strings for proper display in the Dash table
    df = df.astype(str)

    # Create the Dash table
    return dash_table.DataTable(
        id='contact-matrix-table',
        columns=[{"name": "Age Group", "id": "Age Group"}] + [{"name": col, "id": col} for col in df.columns],
        data=[{"Age Group": idx, **row.to_dict()} for idx, row in df.iterrows()],  # Add the index column data
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_data_conditional=[
            {
                'if': {'state': 'active'},  # Apply styles when a cell is hovered
                'backgroundColor': 'lightblue',  # Set hover background color
                'color': 'black',  # Set hover text color
                'border': '2px solid lightblue'
            }
        ]
    )


def generateVaccinationImpactContactPatternsTable():
    """
    Generates a table displaying the impact of vaccination on contact patterns based on age groups.

    This function reads a CSV file containing vaccination impact factors and contact patterns for different age groups. 
    The CSV file includes the following columns:
    - 'Mean Contacts': The average number of contacts in a given time period.
    - 'Standard Deviation': The standard deviation of the contact numbers.
    - '1-14 days after first dose (95% CI)': The 95% confidence interval for contact patterns between 1-14 days after the first dose.
    - '15-28 days after first dose (95% CI)': The 95% confidence interval for contact patterns between 15-28 days after the first dose.

    The function reads the data from a CSV file located in the `data` directory, then generates a Dash DataTable 
    to display this information. The table includes interactive features such as hover effects to highlight the cells when they are active.

    Returns:
    - dash_table.DataTable: A Dash table component displaying the vaccination impact and contact pattern data, 
      with hover effects to enhance user interaction.
    """
    factorsPath = os.path.join(currentDir, "./data/factors.csv")
    df = pd.read_csv(factorsPath)
    return dash_table.DataTable(
            df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], 
            id='vaccination-impact-table', 
            style_data_conditional=[
                {
                    'if': {'state': 'active'},  # Apply styles when a cell is hovered
                    'backgroundColor': 'lightblue',  # Set hover background color
                    'color': 'black',  # Set hover text color
                    'border': '2px solid lightblue'
                }
            ])