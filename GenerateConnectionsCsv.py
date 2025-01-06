import random
import os
import numpy as np
import pandas as pd
import csv
from collections import defaultdict

name = 'infectious.csv'
current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, "./data/{}".format(name))

def assignAgeToIDs(population, rng, ageGroupsDistribution):
    '''
    Assigns ages to a population based on age group proportions.

    Parameters:
        population (int): Total population size.
        rng (numpy.random.Generator): Random number generator for age selection.
        ageGroupsDistribution (list of int): List of proportions for each age group:
            [1-24], [25-44], [45-64], [65-74], [75-100].
            e.g ageGroupsDistribution: [82,82,82,82]

    Returns:
        dict: A dictionary mapping person IDs to randomly assigned ages.
        e.g {1: 17, 2: 6, 3: 19, 4: 8, ... , 91: 30, 92: 31, 93: 37, 94: 30,..., 406: 79, 407: 99, 408: 79, 409: 97, 410: 100}

    Description:
        The function divides the population across five predefined age ranges 
        using the provided proportions. The smallest id will take the smallest age range. 
        Any remaining population after the distribution is assigned to the last age group (75-100).
        Each person is assigned a unique ID and a random age within their group.

    '''
    age_ranges = [
    ((1, 24), ageGroupsDistribution[0]),  # Adjusted to match age group < 25
    ((25, 44), ageGroupsDistribution[1]),  # 25 - 44
    ((45, 64), ageGroupsDistribution[2]),  # 45 - 64
    ((65, 74), ageGroupsDistribution[3]),  # 65 - 74
    ((75, 100), ageGroupsDistribution[4]),  # Adjusted to match age group > 74
    ]

    # Initialize the age dictionary
    age_dict = {}

    # Generate ages for each group
    for (low, high), numindi  in age_ranges:
        for person in range(numindi):
            person_id = len(age_dict) + 1  # Create a unique ID for each person
            age_dict[person_id] = rng.integers(low=low, high=high + 1)
    # If there's any remaining population, assign them to the last group
    remaining = population - len(age_dict)
    for person in range(remaining):
        person_id = len(age_dict) + 1
        age_dict[person_id] = rng.integers(low=age_ranges[-1][1], high=age_ranges[-1][1] + 1)
    return age_dict



def get_mean_sd(age, age_ranges):
    """
    Returns the mean and standard deviation for the given age based on age_ranges.

    Parameters:
        age (int): The age to find the corresponding mean and sd for.
        age_ranges (list of tuples): List of (age_range, (mean, sd)) pairs.

    Returns:
        tuple: (mean, sd) for the age if within a defined range, else (None, None).

    Example:
        For age_ranges = [((1, 4), (10.21, 7.65))] and age = 3, returns (10.21, 7.65).
    """
    for (start, end), (mean, sd) in age_ranges:
        if start <= age <= end:
            return mean, sd
    return None, None



def generate_connections(population, rng, age_dict):
    """
    Generates connections between individuals based on age-specific connection ranges. 
    Each individual is assigned a number of connections based on a normal distribution 
    derived from their age group, and the process stops when no further connections can 
    be made within the defined constraints.

    Parameters:
        population (int): Total population size.
        rng (numpy.random.Generator): Random number generator for selecting connections.
        age_dict (dict): Dictionary mapping person IDs to their corresponding ages.

    Returns:
        set: A set of unique connections, where each connection is represented as a tuple of two person IDs.

    Description:
        - Each person's required number of connections is drawn from a normal distribution 
          with mean and standard deviation based on their age group.
        - Connections are symmetric, meaning if person A is connected to person B, 
          person B is also connected to person A.
        - The connection process ensures individuals meet their required number of connections 
          (specified in `required_connections[i]`).
        - The process terminates when fewer than 15 eligible individuals remain, or no further 
          connections can be made.
    """

    # Define age ranges and corresponding (min, max) connections  this is based on report
    # https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0050074&s=09
    age_ranges = [
        ((1, 4), (10.21, 7.65)),
        ((5, 9), (14.81, 10.09)),
        ((10, 14), (18.22, 12.27)),
        ((15, 19), (17.58, 12.03)),
        ((20, 29), (13.57, 10.60)),
        ((30, 39), (14.14, 10.15)),
        ((40, 49), (13.83, 10.86)),
        ((50, 59), (12.30, 10.23)),
        ((60, 69), (9.21, 7.96)),
        ((70, 100), (6.89, 5.83)),
    ]

    connections = set()
    connections_count = {i: 0 for i in range(1, population + 1)}

    # Generate required number of connections per individual
    required_connections = {}
    for person, age in age_dict.items():
        mean, sd = get_mean_sd(age, age_ranges)
        if mean is None or sd is None:
            raise ValueError(f"Age {age} does not fall into any defined range.")

        # Generate number of connections using normal distribution, based on age group mean and sd, rounded down
        num_connections = 0
        while num_connections < 1: num_connections = int(np.random.normal(mean, sd)) # round down
        required_connections[person] = num_connections


    # Track individuals who still need to meet their required connections
    not_reached_req = set(range(1, population + 1))

    # Continue generating connections
    while not_reached_req or any(connections_count[i] < required_connections[i] for i in range(1, population + 1)):
        # Eligible people are those who haven't exceeded their required connections
        eligible_people = [
            person for person in range(1, population + 1)
            if connections_count[person] < required_connections[person]
        ]

        if len(eligible_people) < 15:
            break  # Exit if fewer than 6 eligible people are available

        # Randomly select two different eligible individuals
        person1, person2 = rng.choice(eligible_people, size=2, replace=False)

        connection = tuple(sorted((person1, person2)))

        # Create the connection if it doesn't already exist
        if connection not in connections:
            connections.add(connection)
            connections_count[person1] += 1
            connections_count[person2] += 1

            # Update the not_reached_req pool
            if connections_count[person1] >=required_connections[person1]:
                not_reached_req.discard(person1)
            if connections_count[person2] >= required_connections[person2]:
                not_reached_req.discard(person2)

    return connections


def GenerateInfectiousSameConnections(population, days, seed, ageGroupsDistribution):
    """
    Generates and writes daily connection data between individuals, considering their age, 
    for a given number of days. The connections are consistent across all days.

    Parameters:
        population (int): Total population size.
        days (int): The number of days to generate connections.
        seed (int): Random seed for reproducibility of connections.
        ageGroupsDistribution (list of int): Distribution of individuals across different age groups 
                                             (e.g., proportions for age groups like 1-24, 25-44, etc.).

    Returns:
        None: Writes daily connection data to a CSV file.

    Description:
        - The function first assigns ages to individuals based on the `ageGroupsDistribution`.
        - It generates a set of connections across the entire population, with each person connected 
          to others based on age-specific mean and standard deviation connections.
        - For each day, the function writes the connections to a CSV file, including the IDs of 
          the two connected individuals and their respective ages.
        - Connections are sorted by person ID for consistency across all days.
        - The connections are the same across all days (static connections).
        - The CSV includes columns for the day, person IDs, and their respective ages for each connection(Day,Person1,Person2,Age1,Age2).
    """
    rng = np.random.default_rng(seed)
    # Generate connections once for all days
    age_dict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    connections = generate_connections(population, rng, age_dict)
    
    # Write connections for each day into the txt file
    with open(path, "w", newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row if desired
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        
        for day in range(1, days + 1):
            sorted_connections = []
            
            # Prepare the sorted list of connections with ages
            for p1, p2 in connections:
                age1 = age_dict[p1]  # age of person1
                age2 = age_dict[p2]  # age of person2
                sorted_connections.append((p1, p2, age1, age2))  # undirected edge
            
            # Sort connections by person1, then by person2
            sorted_connections.sort(key=lambda x: (x[0], x[1]))

            # Write the sorted connections for each day
            for p1, p2, age1, age2 in sorted_connections:
                writer.writerow([day, p1, p2, age1, age2])

    # print("File 'infectious.txt' generated successfully.")


# Set the number of people, connections per day, and days
def GenerateInfectiousUniqueConnections(population, days, seed, ageGroupsDistribution):
    '''
    Generates and writes unique daily connection data between individuals, considering their age, 
    for a given number of days. The connections are distinct across all days.

    Parameters:
        population (int): Total population size.
        days (int): Number of days for which to generate connections.
        seed (int): Random seed for reproducibility.
        ageGroupsDistribution (list of int): Proportions representing the distribution of individuals 
                                             across different age groups.

    Returns:
        None: Writes daily connection data to a CSV file.

    Description:
        - The function first assigns ages to individuals based on the `ageGroupsDistribution`.
        - Daily connections are generated based on age-specific mean and standard deviation connections, and each day contains 
          a new, unique set of connections.
        - Connections are sorted by person ID for consistency across all days.
        - The connections are the unique across all days (dynamic connections).
        - The CSV includes columns for the day, person IDs, and their respective ages for each connection(Day,Person1,Person2,Age1,Age2).
    '''
    # Dictionary to store the age of each person1
    age_dict = {}
    rng = np.random.default_rng(seed)

    # Dictionary to store the age of each person, Assign ages to person
    age_dict = assignAgeToIDs(population, rng, ageGroupsDistribution)

    # Write connections directly to a txt file
    with open(path, mode="w", newline='') as file:
        writer = csv.writer(file)
        # Write the header (optional)
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        for day in range(1, days + 1):
            day_connections = generate_connections(population, rng, age_dict)
            sorted_connections = []

            for p1, p2 in day_connections:
                age1 = age_dict[p1]  # age of person1
                age2 = age_dict[p2]  # age of person2
                
                # Normalize to ensure (p1, p2) is always (min, max)
                p1, p2 = sorted([p1, p2])
                sorted_connections.append((p1, p2, age1, age2))  # undirected edge

            # Sort connections by person1, then by person2
            sorted_connections.sort(key=lambda x: (x[0], x[1]))

            # Write the sorted connections to the file
            for p1, p2, age1, age2 in sorted_connections:
                writer.writerow([day, p1, p2, age1, age2])
    # print("File 'infectious.txt' generated successfully.")




# Generate the complete graph connections
def generate_complete_graph(population):
    """
    Generates a complete graph of connections between all individuals in the population.
    It ensures no duplicate connections by only adding each pair once (person1 < person2)
    Parameters:
        population (int): The total number of individuals.

    Returns:
        list of tuples: A list of unique connections (person1, person2) representing a complete graph, 
                         where each individual is connected to every other individual.
    """
    connections = []
    for person1 in range(1, population + 1):
        for person2 in range(person1 + 1, population + 1):  # Avoid duplicate connections
            connections.append((person1, person2))
    return connections


def GenerateInfectiousCompleteConnections(population, days, seed, ageGroupsDistribution):
    '''
    Generates and writes daily connections for a complete graph of individuals, where every person is 
    connected to every other person. Each person is assigned a consistent age, and the connections are 
    generated for all days based on the complete graph.

    Parameters:
        population (int): Total population size.
        days (int): Number of days for which to generate connections.
        seed (int): Random seed for reproducibility.
        ageGroupsDistribution (list of int): Proportions representing the distribution of individuals 
                                             across different age groups.

    Returns:
        None: Writes daily connection data to a CSV file.

    Description:
        - The function first assigns ages to individuals based on the `ageGroupsDistribution`.
        - It generates a complete graph, where every person is connected to every other person in the population.
        - For each day, the function generates all possible connections between individuals, with their 
          corresponding ages.
        - Connections are sorted by person ID for consistency across all days.
        - The connections are the same across all days (static connections).
        - The CSV includes columns for the day, person IDs, and their respective ages for each connection(Day,Person1,Person2,Age1,Age2).

    '''
    rng = np.random.default_rng(seed)

    # Dictionary to store the age of each person, Assign ages to person
    age_dict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    
    # Get all connections for the complete graph
    complete_connections = generate_complete_graph(population)

    # Write to the CSV file
    with open(path, mode="w", newline='') as file:
        writer = csv.writer(file)
        
        # Write the header (optional)
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        
        for day in range(1, days + 1):
            # Prepare the sorted list of connections with ages for the current day
            sorted_connections = []
            for p1, p2 in complete_connections:
                age1 = age_dict[p1]  # age of person1
                age2 = age_dict[p2]  # age of person2
                sorted_connections.append((p1, p2, age1, age2)) # undirected edge

            # Sort connections by person1, then by person2
            sorted_connections.sort(key=lambda x: (x[0], x[1]))

            # Write connections for the current day
            for p1, p2, age1, age2 in sorted_connections:
                writer.writerow([day, p1, p2, age1, age2])

    #print("File 'infectious_complete_graph.txt' generated successfully.")


def GenerateInfectiousModelConnections(population, days, seed, ageGroupsDistribution):
    '''
    Generates and writes daily connection data between individuals based on pre-existing connections 
    from an external file. Each connection is assigned corresponding ages for the individuals involved. 
    The generated connections are repeated across all days.

    Parameters:
        population (int): Total population size.
        days (int): Number of days for which to generate connections.
        seed (int): Random seed for reproducibility.
        ageGroupsDistribution (list of int): Proportions representing the distribution of individuals 
                                             across different age groups.

    Returns:
        None: Writes daily connection data to a CSV file.

    Description:
        - The function reads pre-defined connections from an external CSV file (`hiddenspreaders.csv`), 
          where each row represents a connection between two individuals (Person1, Person2).
        - Each individual is assigned a consistent age across all days based on their person ID.
        - For each day, the function writes the pre-defined set of connections into the CSV file, including 
          the person IDs and their respective ages.
        - The connections are repeated for each day, and the data is written to the CSV file with columns 
          for the day number, person IDs, and ages.

    '''
    rng = np.random.default_rng(seed)
    age_dict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    data = pd.read_csv('./Epidemic/data/hiddenspreaders.csv')
    connections = []
    for i in range(0,len(data.index)):
        connections.append((data.iloc[i].values[0],data.iloc[i].values[1]))

    # Write connections for each day into the txt file
    with open(path, "w", newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row if desired
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        
        for day in range(1, days + 1):
            sorted_connections = []
            
            # Prepare the sorted list of connections with ages
            for p1, p2 in connections:
                age1 = age_dict[p1]  # age of person1
                age2 = age_dict[p2]  # age of person2
                sorted_connections.append((p1, p2, age1, age2))  # undirected edge
            
            # Sort connections by person1, then by person2
            sorted_connections.sort(key=lambda x: (x[0], x[1]))

            # Write the sorted connections for each day
            for p1, p2, age1, age2 in sorted_connections:
                writer.writerow([day, p1, p2, age1, age2])

    # print("File 'infectious.txt' generated successfully.")