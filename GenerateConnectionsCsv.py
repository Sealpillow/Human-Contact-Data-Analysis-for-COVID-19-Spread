from math import floor
import os
import numpy as np
import csv

name = 'infectious.csv'
currentDir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(currentDir, "./data/{}".format(name))

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
    ageRanges = [
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
    ageDict = {}

    # Generate ages for each group
    for (low, high), numindi  in ageRanges:
        for person in range(numindi):
            personId = len(ageDict) + 1  # Create a unique ID for each person
            ageDict[personId] = rng.integers(low=low, high=high + 1)
    # If there's any remaining population, assign them to the last group
    remaining = population - len(ageDict)
    for person in range(remaining):
        personId = len(ageDict) + 1
        ageDict[personId] = rng.integers(low=ageRanges[-1][1], high=ageRanges[-1][1] + 1)
    return ageDict



def getMeanSd(age, ageRanges):
    """
    Returns the mean and standard deviation for the given age based on ageRanges.

    Parameters:
        age (int): The age to find the corresponding mean and sd for.
        ageRanges (list of tuples): List of (ageRange, (mean, sd)) pairs.

    Returns:
        tuple: (mean, sd) for the age if within a defined range, else (None, None).

    Example:
        For ageRanges = [((1, 4), (10.21, 7.65))] and age = 3, returns (10.21, 7.65).
    """
    for (start, end), (mean, sd) in ageRanges:
        if start <= age <= end:
            return mean, sd
    return None, None

def precomputePools(population):
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
        list of tuples: A list containing tuples of (personId, weight), where 
                        personId ranges from 1 to the population, and each individual 
                        has an equal weight of 1.        
    
    Example:
        >>> precomputePools(5)
        [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    """
    # Precompute pool
    baseWeightedPool = [(person, 1) for person in range(1, population + 1)]
    return baseWeightedPool


def precomputeWeightedPools(population, ageDict):
    """
    Precomputes weighted pools for each age group based on the contact matrix.

    The contact matrix (MFull) represents the rate of contact between each pair 
    of age brackets. These values are used as weights for selecting contacts, 
    meaning individuals will have higher chances of selection based on their 
    contact rate with other age groups.
    It accounts for varying population distributions, especially in the case of a skewed age demographic.

    By adjusting the pool for each age group based on the actual population composition, ensuring more realistic 
    interaction probabilities.
    

    Args:
        population (int): The total number of individuals in the population.
        ageDict (dict): A dictionary mapping individual IDs to their respective age.

    Returns:
        dict: A dictionary where keys represent age groups (0-8), and values are lists 
              of tuples (personId, contactRate), defining the weighted pool for 
              each age group.

    Example:
        >>> precomputeWeightedPools(5, {1: 25, 2: 34, 3: 45, 4: 67, 5: 80})
        { 0: [(1, 3.0), (2, 7.1), (3, 3.7), (4, 2.3), (5, 1.4)], 
          1: [(1, 6.4), (2, 5.4), (3, 7.5), (4, 1.8), (5, 1.7)],  
          ...
        }
    """
    # Contact matrix
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

    # Initialize the weighted pools for each age group
    ageGroupPools = {}
    
    # Precompute weighted pools for each age group
    for age in range(9):  # Age groups 0-8
        weightedPool = []
        for person2 in range(1, population + 1):
            # Determine the age group of person2
            if ageDict[person2] <= 79:
                age2 = floor(ageDict[person2] / 10)
            else:
                age2 = 8  # Age group 80+
            
            # Get the rate of contact between age and age2
            weight = MFull[age, age2]
            weightedPool.append((person2, weight))
        
        # Store the weighted pool for this age group
        ageGroupPools[age] = weightedPool

    return ageGroupPools

def generateConnectionsRandomly(population, rng, baseWeightedPool):
    """
    Generates social connections based on precomputed weighted pools and individual connection requirements.

    This function generates a set of random connections between individuals in a population. Each individual is 
    assigned a required number of connections, which is randomly chosen from a uniform distribution between 1 and 17.
    Connections are made by sampling from a weighted pool, where the weights are determined by the precomputed contact 
    matrix. The function ensures that no individual connects to themselves or has duplicate connections.

    Args:
        population (int): Total number of individuals in the population.
        rng (numpy.random.Generator): A random number generator instance used for generating random values.
        baseWeightedPool (list): A list of tuples representing the precomputed weighted pool, 
                                    where each tuple consists of an individual ID and their associated weight.

    Returns:
        set: A set of connections, where each connection is represented as a tuple of two unique individual IDs.

    Example:
        >>> generateConnectionsRandomly(5, rng, baseWeightedPool)
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
    connectionsCount = {i: 0 for i in range(1, population + 1)}

    # Generate required connections using uniform distribution (1-55)
    requiredConnections = {person: rng.integers(1,19) for person in range(1, population + 1)}

    # Generate connections
    for person1 in range(1, population + 1):
        
        weightedPool = baseWeightedPool

        # Filter the weighted pool to exclude person1 from connecting to himself
        filteredPool = [
            (person, weight) for person, weight in weightedPool
            if person != person1 and (person1, person) not in connections
        ]

        # If there are fewer candidates than required, adjust the required connections
        requiredConnections[person1] = min(requiredConnections[person1], len(filteredPool))

        if not filteredPool:
            print(f"No valid candidates for person {person1}. Skipping.")
            continue
        
        # Normalize the weights for the filtered pool
        totalWeight = sum(weight for _, weight in filteredPool)
        normalizedWeights = [weight / totalWeight for _, weight in filteredPool]

        # Sample connections until the required number is met
        while connectionsCount[person1] < requiredConnections[person1]:
            # Sample a connection from the filtered pool
            person2 = rng.choice(
                [person for person, _ in filteredPool],
                p=normalizedWeights
            )

            # Add the connection
            connection = tuple(sorted((person1, person2)))
            connections.add(connection)
            connectionsCount[person1] += 1
            connectionsCount[person2] += 1

            # Update the filtered pool to exclude person2, to prevent repeated connections
            filteredPool = [
                (person, weight) for person, weight in filteredPool
                if person != person2
            ]

            if not filteredPool:
                print(f"No more valid candidates for person {person1}. Stopping.")
                break

            # Re-normalize the weights for the updated filtered pool
            totalWeight = sum(weight for _, weight in filteredPool)
            normalizedWeights = [weight / totalWeight for _, weight in filteredPool]

    return connections

def generateConnectionsByAgeGroup(population, rng, ageDict, ageGroupPools):
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
        ageDict (dict): A dictionary mapping individual IDs to their ages.
        ageGroupPools (dict): A dictionary mapping age group indices to their corresponding weighted pools,
                                where each pool contains tuples of (individual ID, weight) for that age group.

    Returns:
        set: A set of connections, where each connection is represented as a tuple of two unique individual IDs.

    Example:
        >>> generateConnectionsByAgeGroup(5, rng, ageDict, ageGroupPools)
        {(1, 2), (1, 3), (2, 4), (3, 5)}


    Benefits:
        - Adjusts the connection generation based on age group-specific patterns, ensuring realistic social network modeling.
        - Dynamically filters the weighted pool to avoid duplicate or self-connections.
        - Incorporates real-world age-based variations in social connection patterns by using statistical data.
    """

    # Define age ranges and corresponding (min, max) connections  this is based on report
    # https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0050074&s=09
    ageRanges = [
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
    connectionsCount = {i: 0 for i in range(1, population + 1)}

    # Generate required number of connections per individual
    requiredConnections = {}
    for person, age in ageDict.items():
        mean, sd = getMeanSd(age, ageRanges)
        if mean is None or sd is None:
            raise ValueError(f"Age {age} does not fall into any defined range.")

        # Generate number of connections using normal distribution, based on age group mean and sd, rounded down
        numConnections = 0
        while numConnections < 1: numConnections = int(rng.normal(mean, sd)) # round down
        requiredConnections[person] = numConnections

    # Generate connections
    for person1 in range(1, population + 1):
        # Determine the age group of person1
        if ageDict[person1] <= 79:
            age1 = floor(ageDict[person1] / 10)
        else:
            age1 = 8  # Age group 80+

        # Get the precomputed weighted pool for person1's age group
        weightedPool = ageGroupPools[age1]

        # Filter the weighted pool to exclude person1 from connecting to himself
        filteredPool = [
            (person, weight) for person, weight in weightedPool
            if person != person1 and (person1, person) not in connections
        ]

        # If there are fewer candidates than required, adjust the required connections
        requiredConnections[person1] = min(requiredConnections[person1], len(filteredPool))

        if not filteredPool:
            print(f"No valid candidates for person {person1}. Skipping.")
            continue
        
        # Normalize the weights for the filtered pool
        totalWeight = sum(weight for _, weight in filteredPool)
        normalizedWeights = [weight / totalWeight for _, weight in filteredPool]

        # Sample connections until the required number is met
        while connectionsCount[person1] < requiredConnections[person1]:
            # Sample a connection from the filtered pool
            person2 = rng.choice(
                [person for person, _ in filteredPool],
                p=normalizedWeights
            )

            # Add the connection
            connection = tuple(sorted((person1, person2)))
            connections.add(connection)
            connectionsCount[person1] += 1
            connectionsCount[person2] += 1

            # Update the filtered pool to exclude person2, to prevent repeated connections
            filteredPool = [
                (person, weight) for person, weight in filteredPool
                if person != person2
            ]

            if not filteredPool:
                print(f"No more valid candidates for person {person1}. Stopping.")
                break

            # Re-normalize the weights for the updated filtered pool
            totalWeight = sum(weight for _, weight in filteredPool)
            normalizedWeights = [weight / totalWeight for _, weight in filteredPool]

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
    ageDict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    if 'age' not in checkbox:
        baseWeightedPool = precomputePools(population)
        connections = generateConnectionsRandomly(population, rng, baseWeightedPool)
    else:
        ageGroupPools = precomputeWeightedPools(population, ageDict)
        connections = generateConnectionsByAgeGroup(population, rng, ageDict, ageGroupPools)
    # Open the file in write mode to delete its contents
    with open(path, "w", newline='') as file:
        pass  # No need to write anything, just opening the file empties it

    # Write connections for each day into the txt file
    with open(path, "w", newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row if desired
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        
        for day in range(1, days + 1):
            sortedConnections = []
            
            # Prepare the sorted list of connections with ages
            for p1, p2 in connections:
                age1 = ageDict[p1]  # age of person1
                age2 = ageDict[p2]  # age of person2
                sortedConnections.append((p1, p2, age1, age2))  # undirected edge
            
            # Sort connections by person1, then by person2
            sortedConnections.sort(key=lambda x: (x[0], x[1]))

            # Write the sorted connections for each day
            for p1, p2, age1, age2 in sortedConnections:
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
    ageDict = {}
    rng = np.random.default_rng(seed)

    # Dictionary to store the age of each person, Assign ages to person
    ageDict = assignAgeToIDs(population, rng, ageGroupsDistribution)
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
                baseWeightedPool = precomputePools(population)
                dayConnections = generateConnectionsRandomly(population, rng, baseWeightedPool)
            else:
                ageGroupPools = precomputeWeightedPools(population, ageDict)
                dayConnections = generateConnectionsByAgeGroup(population, rng, ageDict, ageGroupPools)
            sortedConnections = []

            for p1, p2 in dayConnections:
                age1 = ageDict[p1]  # age of person1
                age2 = ageDict[p2]  # age of person2
                
                # Normalize to ensure (p1, p2) is always (min, max)
                p1, p2 = sorted([p1, p2])
                sortedConnections.append((p1, p2, age1, age2))  # undirected edge

            # Sort connections by person1, then by person2
            sortedConnections.sort(key=lambda x: (x[0], x[1]))

            # Write the sorted connections to the file
            for p1, p2, age1, age2 in sortedConnections:
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
    ageDict = assignAgeToIDs(population, rng, ageGroupsDistribution)
    
    # Get all connections for the complete graph
    completeConnections = generateCompleteConnections(population)

    # Write to the CSV file
    with open(path, mode="w", newline='') as file:
        writer = csv.writer(file)
        
        # Write the header (optional)
        writer.writerow(["Day", "Person1", "Person2", "Age1", "Age2"])
        
        for day in range(1, days + 1):
            # Prepare the sorted list of connections with ages for the current day
            sortedConnections = []
            for p1, p2 in completeConnections:
                age1 = ageDict[p1]  # age of person1
                age2 = ageDict[p2]  # age of person2
                sortedConnections.append((p1, p2, age1, age2)) # undirected edge

            # Sort connections by person1, then by person2
            sortedConnections.sort(key=lambda x: (x[0], x[1]))

            # Write connections for the current day
            for p1, p2, age1, age2 in sortedConnections:
                writer.writerow([day, p1, p2, age1, age2])

    #print("File 'infectiousCompleteGraph.txt' generated successfully.")


