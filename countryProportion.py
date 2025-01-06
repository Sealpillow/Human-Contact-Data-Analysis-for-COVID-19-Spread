import pandas as pd
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

def generateProportion(country, year):
    """
    Calculates the proportional population distribution across predefined age groups 
    for a given country and year, ensuring the sum of proportions equals 100%.

    Parameters:
        country (str): The name of the country for which the distribution is calculated.
        year (int): The year for which the distribution is calculated.

    Returns:
        list: A list of integers representing the percentage of the total population 
              in each age group, adjusted to ensure the total sums to 100%.

    Description:
        - Reads population data from a CSV file, filtering for the specified country and year.
        - Age groups are defined as: <25, 25-44, 45-64, 65-74, >74.
        - Calculates the proportion of the population in each age group, 
          rounding to the nearest integer.
        - Adjusts the proportions iteratively to correct for rounding errors 
          while maintaining the total at 100%.
    """
    name = 'population-by-five-year-age-group.csv'
    path = os.path.join(current_dir, "./data/{}".format(name))
    dataCSV = pd.read_csv(path)
    # Age Group: <25, 25 - 44, 45 - 64, 65 - 74, >74
    dataCSV = dataCSV.query(f"Entity == '{country}' and Year == {year}")
    totalPopulation = int(sum(dataCSV.iloc[:, 3:].values[0]))

    specificProportion = [round(sum(dataCSV.iloc[:, 3:8].values[0]/totalPopulation)*100),round(sum(dataCSV.iloc[:, 8:12].values[0]/totalPopulation)*100),
                        round(sum(dataCSV.iloc[:, 12:16].values[0]/totalPopulation)*100),round(sum(dataCSV.iloc[:, 16:18].values[0]/totalPopulation)*100),
                        round(sum(dataCSV.iloc[:, 18:].values[0]/totalPopulation)*100)]
    while(sum(specificProportion)>100): 
        specificProportion[specificProportion.index(max(specificProportion))]-=1
    while(sum(specificProportion)<100): 
        specificProportion[specificProportion.index(min(specificProportion))]+=1

    return specificProportion
     