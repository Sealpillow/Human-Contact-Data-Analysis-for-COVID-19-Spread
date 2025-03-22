from math import floor
import os
import numpy as np
import csv

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
            [0-9], [10-19], [20-29], [30-39], [40-49], [50-59], [60-69], [70-100]
            e.g ageGroupsDistribution: [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5]
            
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
    ((0, 9), ageGroupsDistribution[0]),      # 0-9
    ((10, 19), ageGroupsDistribution[1]),    # 10-19
    ((20, 29), ageGroupsDistribution[2]),    # 20-29
    ((30, 39), ageGroupsDistribution[3]),    # 30-39
    ((40, 49), ageGroupsDistribution[4]),    # 40-49
    ((50, 59), ageGroupsDistribution[5]),    # 50-59
    ((60, 69), ageGroupsDistribution[6]),    # 60-69
    ((70, 100), ageGroupsDistribution[7]),   # >70
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

def precompute_pools(population):
    """
    Precomputes a weighted pool of individuals for random connection generation.

    This function ensures that every individual in the population has an equal chance 
    of being selected for connections. Each individual is assigned a weight of 1, 
    allowing for uniform probability distribution when randomly selecting individuals 
    for interaction or connection.

    Ensures equal probability for every individual to be selected for connections.
    Simplifies the generation of random connections by assigning uniform weights.

    Args:
        population (int): The total number of individuals in the population.

    Returns:
        list of tuples: A list containing tuples of (person_id, weight), where 
                        person_id ranges from 1 to the population, and each individual 
                        has an equal weight of 1.        
    
    Example:
        >>> precompute_pools(5)
        [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    """
    # Precompute pool
    base_weighted_pool = [(person, 1) for person in range(1, population + 1)]
    return base_weighted_pool


def precompute_weighted_pools(population, age_dict):
    """
    Precomputes weighted pools for each age group based on the contact matrix.

    The contact matrix (M_full) represents the rate of contact between each pair 
    of age brackets. These values are used as weights for selecting contacts, 
    meaning individuals will have higher chances of selection based on their 
    contact rate with other age groups.
    It accounts for varying population distributions, especially in the case of a skewed age demographic.

    By adjusting the pool for each age group based on the actual population composition, ensuring more realistic 
    interaction probabilities.
    

    Args:
        population (int): The total number of individuals in the population.
        age_dict (dict): A dictionary mapping individual IDs to their respective age.

    Returns:
        dict: A dictionary where keys represent age groups (0-8), and values are lists 
              of tuples (person_id, contact_rate), defining the weighted pool for 
              each age group.

    Example:
        >>> precompute_weighted_pools(5, {1: 25, 2: 34, 3: 45, 4: 67, 5: 80})
        { 0: [(1, 3.0), (2, 7.1), (3, 3.7), (4, 2.3), (5, 1.4)], 
          1: [(1, 6.4), (2, 5.4), (3, 7.5), (4, 1.8), (5, 1.7)],  
          ...
        }
    """
    # Contact matrix
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

    # Initialize the weighted pools for each age group
    age_group_pools = {}
    
    # Precompute weighted pools for each age group
    for age in range(9):  # Age groups 0-8
        weighted_pool = []
        for person2 in range(1, population + 1):
            # Determine the age group of person2
            if age_dict[person2] <= 79:
                age2 = floor(age_dict[person2] / 10)
            else:
                age2 = 8  # Age group 80+
            
            # Get the rate of contact between age and age2
            weight = M_full[age, age2]
            weighted_pool.append((person2, weight))
        
        # Store the weighted pool for this age group
        age_group_pools[age] = weighted_pool

    return age_group_pools

def generateConnectionsRandomly(population, rng, base_weighted_pool):
    """
    Generates social connections based on precomputed weighted pools and individual connection requirements.

    This function generates a set of random connections between individuals in a population. Each individual is 
    assigned a required number of connections, which is randomly chosen from a uniform distribution between 1 and 17.
    Connections are made by sampling from a weighted pool, where the weights are determined by the precomputed contact 
    matrix. The function ensures that no individual connects to themselves or has duplicate connections.

    Args:
        population (int): Total number of individuals in the population.
        rng (numpy.random.Generator): A random number generator instance used for generating random values.
        base_weighted_pool (list): A list of tuples representing the precomputed weighted pool, 
                                    where each tuple consists of an individual ID and their associated weight.

    Returns:
        set: A set of connections, where each connection is represented as a tuple of two unique individual IDs.

    Example:
        >>> generateConnectionsRandomly(5, rng, base_weighted_pool)
        {(1, 2), (1, 3), (2, 4), (3, 5)}
    
    Notes:
        - The function ensures that each individual has a random number of connections between 1 and 17.
        - Connections are sampled from a weighted pool, where the probability of connecting to each individual is 
          proportional to their precomputed weight.
        - After a connection is formed, the pool is updated to exclude the newly connected individual to avoid repeats.
        - If an individual has no valid candidates to connect to, they are skipped, and no further connections will be 
          generated for that individual.

    Benefits:
        - Ensures diverse and random connections based on precomputed weights.
        - Adjusts connection generation dynamically by filtering out already connected individuals.
        - Handles varying connection requirements per individual.
    """

    connections = set()
    connections_count = {i: 0 for i in range(1, population + 1)}

    # Generate required connections using uniform distribution (1-55)
    required_connections = {person: rng.integers(1,19) for person in range(1, population + 1)}

    # Generate connections
    for person1 in range(1, population + 1):
        
        weighted_pool = base_weighted_pool

        # Filter the weighted pool to exclude person1 from connecting to himself
        filtered_pool = [
            (person, weight) for person, weight in weighted_pool
            if person != person1 and (person1, person) not in connections
        ]

        # If there are fewer candidates than required, adjust the required connections
        required_connections[person1] = min(required_connections[person1], len(filtered_pool))

        if not filtered_pool:
            print(f"No valid candidates for person {person1}. Skipping.")
            continue
        
        # Normalize the weights for the filtered pool
        total_weight = sum(weight for _, weight in filtered_pool)
        normalized_weights = [weight / total_weight for _, weight in filtered_pool]

        # Sample connections until the required number is met
        while connections_count[person1] < required_connections[person1]:
            # Sample a connection from the filtered pool
            person2 = rng.choice(
                [person for person, _ in filtered_pool],
                p=normalized_weights
            )

            # Add the connection
            connection = tuple(sorted((person1, person2)))
            connections.add(connection)
            connections_count[person1] += 1
            connections_count[person2] += 1

            # Update the filtered pool to exclude person2, to prevent repeated connections
            filtered_pool = [
                (person, weight) for person, weight in filtered_pool
                if person != person2
            ]

            if not filtered_pool:
                print(f"No more valid candidates for person {person1}. Stopping.")
                break

            # Re-normalize the weights for the updated filtered pool
            total_weight = sum(weight for _, weight in filtered_pool)
            normalized_weights = [weight / total_weight for _, weight in filtered_pool]

    return connections

def generateConnectionsByAgeGroup(population, rng, age_dict, age_group_pools):
    """
    Generates social connections based on precomputed weighted pools, considering individuals' age groups.

    This function generates social connections between individuals in a population, with the number of connections 
    determined by their age group. The age group-specific connection requirements are based on a normal distribution 
    whose parameters (mean and standard deviation) are derived from age-related statistics. Connections are sampled 
    from precomputed weighted pools for each age group, ensuring no individual connects to themselves or forms duplicate 
    connections.

    Args:
        population (int): Total number of individuals in the population.
        rng (numpy.random.Generator): Random number generator instance used for generating random values.
        age_dict (dict): A dictionary mapping individual IDs to their ages.
        age_group_pools (dict): A dictionary mapping age group indices to their corresponding weighted pools,
                                where each pool contains tuples of (individual ID, weight) for that age group.

    Returns:
        set: A set of connections, where each connection is represented as a tuple of two unique individual IDs.

    Example:
        >>> generateConnectionsByAgeGroup(5, rng, age_dict, age_group_pools)
        {(1, 2), (1, 3), (2, 4), (3, 5)}


    Benefits:
        - Adjusts the connection generation based on age group-specific patterns, ensuring realistic social network modeling.
        - Dynamically filters the weighted pool to avoid duplicate or self-connections.
        - Incorporates real-world age-based variations in social connection patterns by using statistical data.
    """

    # Define age ranges and corresponding (min, max) connections  this is based on report
    # https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0050074&s=09
    age_ranges = [
        ((0, 4), (10.21, 7.65)),
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
        while num_connections < 1: num_connections = int(rng.normal(mean, sd)) # round down
        required_connections[person] = num_connections

    # Generate connections
    for person1 in range(1, population + 1):
        # Determine the age group of person1
        if age_dict[person1] <= 79:
            age1 = floor(age_dict[person1] / 10)
        else:
            age1 = 8  # Age group 80+

        # Get the precomputed weighted pool for person1's age group
        weighted_pool = age_group_pools[age1]

        # Filter the weighted pool to exclude person1 from connecting to himself
        filtered_pool = [
            (person, weight) for person, weight in weighted_pool
            if person != person1 and (person1, person) not in connections
        ]

        # If there are fewer candidates than required, adjust the required connections
        required_connections[person1] = min(required_connections[person1], len(filtered_pool))

        if not filtered_pool:
            print(f"No valid candidates for person {person1}. Skipping.")
            continue
        
        # Normalize the weights for the filtered pool
        total_weight = sum(weight for _, weight in filtered_pool)
        normalized_weights = [weight / total_weight for _, weight in filtered_pool]

        # Sample connections until the required number is met
        while connections_count[person1] < required_connections[person1]:
            # Sample a connection from the filtered pool
            person2 = rng.choice(
                [person for person, _ in filtered_pool],
                p=normalized_weights
            )

            # Add the connection
            connection = tuple(sorted((person1, person2)))
            connections.add(connection)
            connections_count[person1] += 1
            connections_count[person2] += 1

            # Update the filtered pool to exclude person2, to prevent repeated connections
            filtered_pool = [
                (person, weight) for person, weight in filtered_pool
                if person != person2
            ]

            if not filtered_pool:
                print(f"No more valid candidates for person {person1}. Stopping.")
                break

            # Re-normalize the weights for the updated filtered pool
            total_weight = sum(weight for _, weight in filtered_pool)
            normalized_weights = [weight / total_weight for _, weight in filtered_pool]

    return connections

def GenerateInfectiousSameConnections(population, days, seed, ageGroupsDistribution, checkbox):
    """
    Generates a network of infectious connections that remain the same for all days.

    This function simulates daily contacts between individuals based on a given population, 
    their age distribution, and optional age-based grouping. The generated connections 
    are saved to a CSV file, maintaining the same connections for all days.

    Args:
        population (int): The total number of individuals.
        days (int): The number of days for which the connections should be generated.
        seed (int): A seed value for the random number generator to ensure reproducibility.
        ageGroupsDistribution (dict): A dictionary specifying the distribution of age groups in the population.
        checkbox (list): A list of options that determine connection generation behavior 
                         (e.g., whether to consider age groups when forming connections).

    Returns:
        None: The function writes the generated connections to a CSV file and does not return any values.

    Process:
        1. Assigns an age group to each individual in the population.
        2. Generates connections randomly or based on age groups, depending on the checkbox input.
        3. Writes the connections for each day to a CSV file, ensuring they remain constant over time.
        4. Connections are sorted by individual IDs for consistency.
    """
    rng = np.random.default_rng(seed)
    # Generate connections once for all days
    age_dict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    if 'age' not in checkbox:
        base_weighted_pool = precompute_pools(population)
        connections = generateConnectionsRandomly(population, rng, base_weighted_pool)
    else:
        age_group_pools = precompute_weighted_pools(population, age_dict)
        connections = generateConnectionsByAgeGroup(population, rng, age_dict, age_group_pools)
    # Open the file in write mode to delete its contents
    with open(path, "w", newline='') as file:
        pass  # No need to write anything, just opening the file empties it

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
  


# Set the number of people, connections per day, and days
def GenerateInfectiousUniqueConnections(population, days, seed, ageGroupsDistribution, checkbox):
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
    # Open the file in write mode to delete its contents
    with open(path, "w", newline='') as file:
        pass  # No need to write anything, just opening the file empties it 
    # Write connections directly to a txt file
    with open(path, mode="w", newline='') as file:
        writer = csv.writer(file)
        # Write the header (optional)
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        for day in range(1, days + 1):
            if 'age' not in checkbox:
                base_weighted_pool = precompute_pools(population)
                day_connections = generateConnectionsRandomly(population, rng, base_weighted_pool)
            else:
                age_group_pools = precompute_weighted_pools(population, age_dict)
                day_connections = generateConnectionsByAgeGroup(population, rng, age_dict, age_group_pools)
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




# Generate the complete graph connections
def generateCompleteConnections(population):
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
    complete_connections = generateCompleteConnections(population)

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


