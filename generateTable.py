from dash import dash_table
import pandas as pd
import numpy as np
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

def generate_contact_matrix_table():
    # Example contact matrix data
    M_full = np.array([
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

    # Sum of all contacts
    total_contacts = np.sum(M_full)

    # Normalize the matrix to get the probability
    M_prob = M_full / total_contacts

    # Round to 2 decimal places
    M_full_percentage_rounded = np.round(M_prob * 100, 2)

    # Define the index labels
    index_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

    # Create a DataFrame with the appropriate index
    df = pd.DataFrame(M_full_percentage_rounded, index=index_labels, columns=index_labels)

    # Convert the DataFrame values to strings with '%' sign for proper display in the Dash table
    df = df.map(lambda x: f'{x:.2f}%')

    return dash_table.DataTable(
        id='contact-matrix-table',
        columns=[{"name": "Age Group", "id": "Age Group"}] + [{"name": col, "id": col} for col in df.columns],
        data=[{"Age Group": idx, **row} for idx, row in df.iterrows()],  # Add the index column data
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_data_conditional=[
            {
                'if': {'state': 'active'},  # Apply styles when a cell is hovered
                'backgroundColor': 'lightblue',  # Set hover background color
                'color': 'black',  # Set hover text color
                'border': '2px solid lightblue'
            }
        ])



def generate_vaccination_impact_contact_patterns_table():
    factors_path = os.path.join(current_dir, "./data/factors.csv")
    df = pd.read_csv(factors_path)
    return dash_table.DataTable(
            df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], 
            id='tbl',
            style_data_conditional=[
                {
                    'if': {'state': 'active'},  # Apply styles when a cell is hovered
                    'backgroundColor': 'lightblue',  # Set hover background color
                    'color': 'black',  # Set hover text color
                    'border': '2px solid lightblue'
                }
            ])