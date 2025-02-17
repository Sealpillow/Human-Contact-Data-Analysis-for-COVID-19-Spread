import numpy as np
import os 
import math
from scipy.integrate import quad
from plotGraph import plotResult, plotStackBar, plotAgeGroup, plotInfectionRate, plotDegreeVsInfection
from scipy.stats import lognorm, norm
from Network import Network
from Node import Node
from DailyNetworks import DailyNetworks
from GenerateConnectionsCsv import GenerateInfectiousUniqueConnections, GenerateInfectiousSameConnections, GenerateInfectiousCompleteConnections
import json
import sys
import jsonpickle
import csv
from collections import Counter
statusPath = "./data/status.json"

def getData(name, days):
    """
    Reads connection data from a CSV file and constructs a daily network of individuals. Each row in the 
    CSV represents a connection between two individuals on a specific day, including their respective ages.

    Args:
        name (str): The filename of the CSV data to be processed.
        days (int): The number of days for which the networks need to be created.

    Returns:
        DailyNetworks: A DailyNetworks object containing networks for each day, with nodes and connections 
        added based on the CSV data.

    Description:
        - The function initializes a `DailyNetworks` object to hold the networks for each day.
        - For each day in the range from 1 to `days`, it creates a new `Network` and adds it to the 
          `DailyNetworks` object.
        - The CSV file is expected to have the following columns:
            - Day (int): The day of the interaction.
            - Person1 (int): The ID of the first individual in the interaction.
            - Person2 (int): The ID of the second individual in the interaction.
            - Age1 (int): The age of the first individual.
            - Age2 (int): The age of the second individual.
        - For each row in the CSV:
            - It checks if the individuals already exist as nodes in the network for the current day. If they do not, 
              it creates new `Node` objects for them, assigning their infection rate based on their age.
            - It adds connections between the two individuals, ensuring that the relationship is undirected (both 
              individuals are connected to each other).
        - Update each network with the total connection for the calculation of beta value
        - After processing all rows, the function returns the populated `DailyNetworks` object with nodes and connections 
          for each day.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "./data/{}".format(name))

    # ...populate network...
    dailyNetworks = DailyNetworks()
    for day in range(1, days+1):
        newNetwork = Network()
        dailyNetworks.addNetworkByDay(day, newNetwork)
        currNetwork = dailyNetworks.getNetworkByDay(day)

    with open(path, 'r') as infile:
        reader = csv.reader(infile)
        # Skip the header if it exists
        next(reader, None)
        
        for line in reader:
            # Strip any trailing whitespace and assign the columns to variables
            day, person1, person2, age1, age2 = map(int, line)
            if day > days:
                return dailyNetworks 

            currNetwork = dailyNetworks.getNetworkByDay(day)
            if person1 not in currNetwork.getNodes().keys():
                newNode1 = Node(person1, day, age1)      # create Node1
                newNode1.avgConnectionByAge = getAgeGroupConnections(newNode1.age)
                currNetwork.addNode(newNode1)            # add the new node
            else:
                newNode1 = currNetwork.getNode(person1)

                
            if person2 not in currNetwork.getNodes().keys():    
                newNode2 = Node(person2, day, age2)  # create Node2
                newNode2.avgConnectionByAge = getAgeGroupConnections(newNode2.age)
                currNetwork.addNode(newNode2)            # add the new node 
            else:
                newNode2 = currNetwork.getNode(person2)
            newNode1.addConnection(person2)
            newNode2.addConnection(person1)
    # update total connections for each network, for calculation
    for day in range(1, days+1):    
        totalConnections = 0    
        for person in dailyNetworks.getNetworkByDay(day).getNodes().values():
            totalConnections += len(person.getConnections())  # count the total number of connections in then network -> edges
        dailyNetworks.getNetworkByDay(day).totalConnections = totalConnections

    return dailyNetworks
    

def getAgeGroupConnections(age):
    """
    Returns the average number of connections associated with the individual's age group.

    Parameters:
    - age (int): The age of the individual.
    0-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, >70
    Returns:
    - float: The average number of connections for the given age group.
    """
    
    if age < 5:
        return 10.21
    elif 5 <= age <= 9:
        return 14.81   
    elif 10 <= age <= 14:
        return 18.22
    elif 15 <= age <= 19:
        return 17.58  
    elif 20 <= age <= 29:
        return 13.57
    elif 30 <= age <= 39:
        return 14.14 
    elif 40 <= age <= 49:
        return 13.83 
    elif 50 <= age <= 59:
        return 12.30 
    elif 60 <= age <= 69:
        return 9.21 
    else: # If the individual's age is greater than and equal to 70
        return 6.89  



def update_network(day):   # Check the current day network if any one is in infected state-> isolate -> remove the person's connections
    """
    Updates the network for the given day by isolating individuals in the 'infected' state.

    This function checks the network for the current day. If any individual is in the 'infected' state,
    it isolates them by removing all their connections. Isolation begins after the intervention day.

    Parameters:
    - day (int): The current day of the simulation.

    Returns:
    - None: The function modifies the global `dailyNetwork` object directly.
    """
    global dailyNetwork

    # Check if the current day is after the intervention day
    # Isolation of infectious individuals begins only after the intervention day.
    if day + 1 > interventionDay:
        # Retrieve the current day's network and all nodes (individuals) in it
        currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()

        # Iterate through each person in the network
        for person in currentNetworkNodes.values():
            # Check if the person is in the 'infected' state and still has connections
            if person.status == 'I' and len(person.getConnections()) > 0:
                # Isolate the infected individual by removing all their connections
                # This involves breaking all edges (both from and to the node)
                person.removeConnection(currentNetworkNodes)



# Compute the CDFs F_P(d), F_I(d), and F_A(d)
def F_P(d):
    meanP = 1.43                                            # Mean of the underlying normal distribution
    stdP = 0.66                                             # Standard deviation of the underlying normal distribution 
    return lognorm(s=meanP, scale=np.exp(stdP)).cdf(d)


def F_I(d):
    meanI = 8.8                                             # Mean
    stdI = 3.88                                             # Standard deviation
    return norm(loc=meanI, scale=stdI).cdf(d) #


def F_A(d):
    meanA = 20.0                                            # Mean
    stdA = 5.0                                              # Standard deviation
    return norm(loc=meanA, scale=stdA).cdf(d) 


def Beta(day, person):
    """
    Calculates the transmission rate (beta) for an individual on a given day based on various factors, 
    including reproduction number, average network connections, and vaccination status.

    Parameters:
    - day (int): The current day of the simulation.
    - person (object): The individual for whom the transmission rate is being calculated. 
      It is expected that the `person` object has a `vaccinated` attribute.

    Returns:
    - beta (float): The calculated transmission rate for the individual.
    """
    global dailyNetwork, population, p, checkbox, overallReproNum

    # Basic reproduction number (R₀)
    reproNum = overallReproNum

    # Average time periods the virus is carried in different states:
    meanA = 20.0  # State A: Asymptomatic carrier
    meanP = 1.43  # State P: Presymptomatic carrier
    meanI = 8.8   # State I: Symptomatic and infectious
    sigma_P = 0.66  # Standard deviation of virus duration in state P

    # Retrieve the network for the current day
    currNetwork = dailyNetwork.getNetworkByDay(day)

    # Calculate the average number of neighbors in the network
    avgNumNeighNet_k = currNetwork.totalConnections / population

    # Average time a susceptible individual is exposed to the virus
    # Includes contributions from asymptomatic (meanA), presymptomatic (meanP), and symptomatic (meanI) states
    avgtimesusceptible_lambda = p * meanA + (1 - p) * (math.exp(meanP + (sigma_P**2) / 2) + meanI)
    
    # Adjust the reproduction number based on vaccination status
    # Reference: https://www.sciencedirect.com/science/article/pii/S0140673621004487?pes=vor&utm_source=tfo&getft_integrator=tfo
    if 'vaccination' in checkbox and person.vaccinated == True:
        # If vaccination is within the first 14 days after the intervention, reduce R₀ by 30%
        if 1 <= day - interventionDay <= 14:
            reproNum *= (1 - 0.3)
        # If more than 15 days have passed since vaccination, reduce R₀ by 75%
        elif day - interventionDay >= 15:
            reproNum *= (1 - 0.75)   

    # Calculate the transmission rate (beta)
    beta = reproNum / (avgtimesusceptible_lambda * avgNumNeighNet_k)
    return beta

def F(t, j, beta):
    """
    Calculates the infection probability from an infectious node `j` to a single susceptible neighbor 
    on day `t`, scaled by the transmission rate `beta`.

    Parameters:
    - t (int): The current day in the simulation.
    - j (int or str): The ID of the infectious node contributing to the probability.
    - beta (float): The transmission rate representing the likelihood of infection spread.

    Returns:
    - float: The infection probability from node `j` to a single susceptible neighbor on day `t`.
    """
    #  from the report 
    #  Ci(t): total probability corresponds to that of a node is infectious
    #  Ci(t) = Pi(t) + Ii(t) + Ai(t)
    #  F(t,j,β) = Cj(t)·β
    global dailyNetwork
    return dailyNetwork.getNetworkByDay(t).getNode(j).C * beta

def getLatestPeriod(status, personID, day):
    """
    Calculates the most recent consecutive period (in days) that a person with a given `personID`
    has remained in a specific `status` (e.g., 'P', 'A', 'I') up to a given `day`.

    Parameters:
    - status (str): The target status to check (e.g., 'P' for presymtomatic, 'A' for asymtomatic).
    - personID (int or str): The unique identifier of the person whose status is being checked.
    - day (int): The current day in the simulation to begin the backward search.

    Returns:
    - int: The number of consecutive days (including the current day) the person has remained
           in the specified `status`.
    """

    global dailyNetwork
    count = 0  # Counter to track consecutive days in the specified status

    # Iterate backward from the given day to day 1
    for d in range(day, 0, -1):
        # Retrieve the person's status on the given day
        xStatus = dailyNetwork.getNetworkByDay(d).getNode(personID).status

        # If the status differs from the target status, stop the count and return the result
        if xStatus != status:
            return count
        else:
            # Increment the counter if the status matches the target status
            count += 1

    # Return the count if the loop completes (i.e., the status remained constant back to day 1)
    return count


def sumProb(personID, day, state):
    """
    Calculates the cumulative probability of a person being in a specified state ('P', 'A', or 'I') 
    over all days from day 1 to the specified `day`.

    Parameters:
    - personID (int or str): The unique identifier of the person whose probabilities are being summed.
    - day (int): The current day in the simulation up to which the probabilities are calculated.
    - state (str): The target state for which probabilities are summed. Valid values:
      - 'P': Presymptomatic state
      - 'A': Asymptomatic state
      - 'I': Infectious state

    Returns:
    - float: The sum of probabilities associated with the specified state for the given person 
             from day 1 to the specified `day`.

    """

    global dailyNetwork, checkbox  # Dependency on the global network and checkbox variables

    prob = 0  # Initialize the cumulative probability to 0

    # Iterate through each day from the specified `day` backward to day 1
    for d in range(day, 0, -1):
        # Retrieve the node (person) data for the given day and personID
        node = dailyNetwork.getNetworkByDay(d).getNode(personID)

        # Add the corresponding probability based on the specified state
        if state == 'P':  # Presymptomatic state
            prob += node.P
        elif state == 'A':  # Asymptomatic state
            prob += node.A
        elif state == 'I':  # Infectious state
            prob += node.I

    # Return the cumulative probability
    return prob

# Update probabilities for the next day
def update_probabilities(day):
    """
    Updates the probabilities for all individuals in the network for the next day based on 
    their current state (S, P, I, A, or R) and interactions with their connections.

    Parameters:
    - day (int): The current day in the simulation for which probabilities are being updated.

    Dependencies:
    - Uses the global variables:
        - `dailyNetwork`: The network of nodes (individuals) across days.
        - `p`: Probability of asymptomatic infection.
        - `checkbox`: A global variable for optional features (e.g., vaccination effects).

    Steps:
    1. Iterate through all individuals in the network for the current day.
    2. Update probabilities for the next day (`day + 1`) based on the individual's state:
       - **S (Susceptible)**: Probabilities are updated based on infection risk from neighbors.
       - **P (Presymptomatic)**: Probabilities are updated based on the transition to the I (Infectious) state.
       - **I (Infectious)**: Probabilities are updated based on the transition to the R (Recovered) state.
       - **A (Asymptomatic)**: Probabilities are updated based on the transition to the R (Recovered) state.
    3. Update the combined probability `C` (infectiousness) for the next day.

    """

    global dailyNetwork, p, checkbox  # Global dependencies

    # Get all nodes (individuals) in the current day's network
    currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()

    # Iterate through all individuals in the network
    for person in currentNetworkNodes.values():
        # Get the corresponding node for the next day
        personNextDay = dailyNetwork.getNetworkByDay(day + 1).getNode(person.id)

        # If the person is Susceptible (S)
        if person.status == 'S':
            # Calculate infection probability based on connections
            connections = person.getConnections()
            NotInfectedByNeighbourProb = np.prod([(1 - F(day, connection, Beta(day, person))) for connection in connections])
            infectionProb = 1 - NotInfectedByNeighbourProb
            
            # Update probabilities for the next day
            personNextDay.P = person.S * (1 - p) * infectionProb  # Probability of transitioning to P (Presymptomatic)
            personNextDay.A = person.S * p * infectionProb        # Probability of transitioning to A (Asymptomatic)
            personNextDay.S = 1 - personNextDay.P - personNextDay.A  # Remaining probability stays in S

        # If the person is Presymptomatic (P)
        elif person.status == 'P':
            d = getLatestPeriod('P', person.id, day)  # Duration in P state
            personNextDay.I = (sumProb(person.id, day, 'P') * (F_P(d) - F_P(d-1)) / (1 - F_P(d-1)))  # Probability of transitioning to I (Infectious)
            personNextDay.P = 1 - personNextDay.I  # Remaining probability stays in P

        # If the person is Infectious (I)
        elif person.status == 'I':
            d = getLatestPeriod('I', person.id, day)  # Duration in I state
            personNextDay.R = person.R + (sumProb(person.id, day, 'I') * (F_I(d) - F_I(d-1)) / (1 - F_I(d-1)))  # Probability of transitioning to R (Recovered)
            personNextDay.I = 1 - personNextDay.R  # Remaining probability stays in I

        # If the person is Asymptomatic (A)
        elif person.status == 'A':
            d = getLatestPeriod('A', person.id, day)  # Duration in A state
            personNextDay.R = person.R + (sumProb(person.id, day, 'A') * (F_A(d) - F_A(d-1)) / (1 - F_A(d-1)))  # Probability of transitioning to R (Recovered)
            personNextDay.A = 1 - personNextDay.R  # Remaining probability stays in A

        # Update the combined probability for the next day
        personNextDay.C = personNextDay.P + personNextDay.I + personNextDay.A




def update_status(day, rng):
    """
    Updates the status of each individual in the network for the next day based on their current state (S, P, I, A, R).
    The function also handles the process of vaccination after a specific intervention day.

    Parameters:
    - day (int): The current day in the simulation.
    - rng (random generator): A random number generator to roll probabilities.

    Dependencies:
    - Uses global variables:
        - `dailyNetwork`: A collection of individuals' states across different days.
        - `interventionDay`: The day when vaccination starts.
        - `checkbox`: A variable to determine if vaccination is enabled.
        - `vaccinatedHistoryList`: A list to keep track of people who have been vaccinated.
        - `percentVac`: The percentage of the population to vaccinate per day.

    Steps:
    1. Iterate through all individuals in the network for the current day.
    2. Update each individual's status based on their current state (S, P, I, A, or R):
       - **S (Susceptible)**: Person may transition to P (Presymptomatic) or A (Asymptomatic) based on probabilities.
       - **P (Presymptomatic)**: Person may transition to I (Infectious) based on probabilities.
       - **I (Infectious)**: Person may transition to R (Recovered) based on probabilities.
       - **A (Asymptomatic)**: Person may transition to R (Recovered) based on probabilities.
       - **R (Recovered)**: Person stays in the R state (could be reconsidered for reinfection based on the model).
    3. After updating status, check if the intervention day (vaccination) has arrived and proceed with vaccination:
       - Vaccinate the top percentage of susceptible individuals based on age, ensuring no person is vaccinated twice.
       
    """
    global dailyNetwork, interventionDay, checkbox, vaccinatedHistoryList, percentVac
    currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()

    # Iterate through each person in the network
    for person in currentNetworkNodes.values():
        personNextDay = dailyNetwork.getNetworkByDay(day + 1).getNode(person.id)
        rand = rng.random()  # Generate a random number for probability comparison

        # If the person is Susceptible (S)
        if person.status == 'S':
            if rand < personNextDay.P:
                # Transition to Presymptomatic (P)
                personNextDay.status = 'P'
                personNextDay.P = 1
                personNextDay.S = 0
                personNextDay.A = 0
            elif rand < personNextDay.P + personNextDay.A:
                # Transition to Asymptomatic (A)
                personNextDay.status = 'A'
                personNextDay.P = 0
                personNextDay.S = 0
                personNextDay.A = 1
            else:
                # Stay Susceptible
                personNextDay.status = 'S'

        # If the person is Presymptomatic (P)
        elif person.status == 'P':
            if rand < personNextDay.I:
                # Transition to Infectious (I)
                personNextDay.status = 'I'
                personNextDay.I = 1
                personNextDay.P = 0
            else:
                # Stay Presymptomatic
                personNextDay.status = 'P'

        # If the person is Infectious (I)
        elif person.status == 'I':
            if rand < personNextDay.R:
                # Transition to Recovered (R)
                personNextDay.status = 'R'
                personNextDay.R = 1
                personNextDay.I = 0
            else:
                # Stay Infectious
                personNextDay.status = 'I'

        # If the person is Asymptomatic (A)
        elif person.status == 'A':
            if rand < personNextDay.R:
                # Transition to Recovered (R)
                personNextDay.status = 'R'
                personNextDay.R = 1
                personNextDay.A = 0
            else:
                # Stay Asymptomatic
                personNextDay.status = 'A'

        # If the person is Recovered (R)
        else:
            # Stay Recovered (R)
            personNextDay.status = 'R'
            personNextDay.R = 1

    # Handle vaccination after the intervention day
    if 'vaccination' in checkbox and day + 1 >= interventionDay:
        vaccinationRate = percentVac / 100  # Calculate the daily vaccination rate
        sortedPeopleByAge = dailyNetwork.getNetworkByDay(day + 1).getSortedNodeListByAge()

        # Calculate the number of people to vaccinate
        numPeopleToVaccinate = round(population * vaccinationRate)

        for personNextDay in sortedPeopleByAge:
            if personNextDay.status == 'S' and not personNextDay.vaccinated:
                if personNextDay.id not in vaccinatedHistoryList:
                    # Mark as vaccinated and reduce the number of people to vaccinate
                    personNextDay.vaccinated = True
                    numPeopleToVaccinate -= 1
                    vaccinatedHistoryList.append(personNextDay.id)
                else:
                    # Person was already vaccinated in the past
                    personNextDay.vaccinated = True

            # Stop when the required number of people are vaccinated
            if numPeopleToVaccinate == 0:
                break

 


def simulate(seed, population, days, randomNumPeople):
    """
    Simulates the spread of an infectious disease within a population over a given number of days.
    The simulation involves the random assignment of initial infected individuals, disease progression,
    and updates to individual statuses based on probabilistic transitions.

    Parameters:
    - seed (int): The random seed used to initialize the random number generator for reproducibility.
    - population (int): The total number of individuals in the population.
    - days (int): The number of days to run the simulation.
    - randomNumPeople (int): The number of initial spreaders (infected individuals) randomly selected.

    Returns:
    - dailyNetwork (object): The network object containing the population and the status of each individual across days.
    - infectionPlot (plot): A plot showing the count of susceptible, presymptomatic, asymptomatic, infected, and recovered individuals over time.
    - stackBarPlot (plot): A stacked bar plot displaying the status distribution of individuals at each time step.
    - infectionRatePlot (plot): A plot showing the infection rate over time.
    - overallInfectionRate (float): The overall infection rate throughout the simulation.
    - dayInfectionRateList (list): A list of infection rates for each day in the simulation.
    """
    global dailyNetwork, p, checkbox

    # Initialize the random number generator for reproducibility
    rng = np.random.default_rng(seed)

    # Initialize the network for day 1 and randomize infected people
    initialNetwork = dailyNetwork.getNetworkByDay(1)

    # Randomly choose `randomNumPeople` individuals with the highest connections to be the origin spreaders
    numbers = initialNetwork.getListOfHighestConnections(randomNumPeople)
    originSpreaders = rng.choice(numbers, size=randomNumPeople, replace=False)

    # Assign initial statuses to individuals: either infected or susceptible
    for id in range(1, population+1):
        node = initialNetwork.getNode(id)
        if id in originSpreaders:  # If the person is one of the origin spreaders
            rand = rng.random()  # Randomly determine if the person is asymptomatic (A) or presymptomatic (P)
            if rand < p:
                node.status = 'A'  # Asymptomatic
                node.A = 1
            else:
                node.status = 'P'  # Presymptomatic
                node.P = 1
        else:
            node.status = 'S'  # Susceptible
            node.S = 1

    # Initialize lists to track the number of individuals in each state over time
    susceptible_counts = []
    presymptomatic_counts = []
    asymptomatic_counts = []
    infected_counts = []
    recovered_counts = []

    # Run the simulation for each day
    for day in range(1, days+1):
        if day < days:  # Update probabilities until the last day
            if 'isolate' in checkbox:
                update_network(day)  # Isolate infectious individuals
            update_probabilities(day)  # Update infection probabilities
            update_status(day, rng)  # Update individual statuses based on the probabilities

        # Count the number of individuals in each state for the current day
        currentNodes = dailyNetwork.getNetworkByDay(day).getNodes()
        susceptible_counts.append(sum(1 for person in currentNodes.values() if person.status == 'S'))
        presymptomatic_counts.append(sum(1 for person in currentNodes.values() if person.status == 'P'))
        asymptomatic_counts.append(sum(1 for person in currentNodes.values() if person.status == 'A'))
        infected_counts.append(sum(1 for person in currentNodes.values() if person.status == 'I'))
        recovered_counts.append(sum(1 for person in currentNodes.values() if person.status == 'R'))

        # Update the simulation progress in a status file
        with open(statusPath, 'r') as file:
            status = json.load(file)
            status['progress'] = round(day / days * 100)  # Update the progress percentage

        with open(statusPath, 'w') as file:
            json.dump(status, file, indent=4)  # Save the updated progress

    # Plot the results
    degreeVsInfectionPlot, truePositiveRatePlot = plotDegreeVsInfection(dailyNetwork, population, days)
    infectionPlot = plotResult(days, susceptible_counts, presymptomatic_counts, asymptomatic_counts, infected_counts, recovered_counts)
    infectionRatePlot, overallInfectionRate, dayInfectionRateList = plotInfectionRate(days, susceptible_counts)
    stackBarPlot = plotStackBar(days, susceptible_counts, presymptomatic_counts, asymptomatic_counts, infected_counts, recovered_counts)
    avgDailyConnectionsList = dailyNetwork.getAvgDailyConnectionsList()


    return dailyNetwork, infectionPlot, stackBarPlot, infectionRatePlot, degreeVsInfectionPlot, truePositiveRatePlot, overallInfectionRate, dayInfectionRateList, avgDailyConnectionsList


def main():
    """
    The main function to initialize parameters, generate contact networks, and simulate the spread of an infectious disease within a population.
    This function reads command-line arguments to configure the simulation, generates the contact network based on the chosen model (e.g., 'same', 'dynamic', 'complete'),
    and runs the simulation over a specified number of days. During the simulation, various factors like vaccination, isolation, and age groups are considered.
    The simulation results, including the network data, infection statistics, and plots, are serialized into JSON format and printed to the console for further processing by the Dash app.

    The function handles several models for network generation and simulates disease spread over a set number of days. It also tracks
    the vaccination status of individuals and stores various simulation outputs for further analysis.

    Parameters:
    - Command-line arguments are used to configure the following simulation parameters:
      - seed (int): The random seed for reproducibility.
      - overallReproNum (float): The overall reproduction number for the disease.
      - population (int): The number of individuals in the population.
      - days (int): The number of days for the simulation.
      - affected (int): The number of initial infected individuals.
      - interventionDay (int): The day on which vaccination or other interventions start.
      - percentVac (float): The percentage of individuals vaccinated per day.
      - radio (str): The type of connection model used ('same', 'dynamic', 'complete').
      - proportion (list of ints): The age group proportions in the population.
      - checkbox (list of str): A list of additional options (e.g., 'age', 'isolate').

    Returns:
    - result (dict): A dictionary containing the simulation results, including:
        - 'days': The number of days in the simulation.
        - 'dailyNetwork': The serialized network data for each day.
        - 'infectionGraph': The serialized infection plot.
        - 'populationPie': The serialized pie chart of age group distribution.
        - 'stackBarPlot': The serialized stacked bar plot of population status.
        - 'infectionRatePlot': The serialized infection rate plot.
        - 'overallInfectionRate': The overall infection rate throughout the simulation.
        - 'dayInfectionRateList': A list of infection rates for each day.
    """
    global dailyNetwork, population, days, seed, overallReproNum, p, interventionDay, checkbox, vaccinatedHistoryList, percentVac

    '''
    seed = 123
    overallReproNum = 3.5
    population = 200
    days = 100
    affected = 5
    interventionDay = 0
    percentVac = 1
    radio = 'same'
    proportion = [12.5,12.5,12.5,12.5,12.5,12.5,12.5,12.5]
    checkbox = []
    '''
    # Read command-line arguments to initialize simulation parameters
    seed = int(sys.argv[1])  # Set the random seed for reproducibility
    overallReproNum = float(sys.argv[2])  # Set the overall reproduction number
    population = int(sys.argv[3])  # Set the population size
    days = int(sys.argv[4])  # Set the number of days for the simulation
    affected = int(sys.argv[5])  # Set the number of initially infected individuals
    interventionDay = int(sys.argv[6])  # Set the day when vaccination starts
    percentVac = float(sys.argv[7])  # Set the percentage of the population vaccinated per day
    radio = sys.argv[8]  # Set the connection model type
    proportion = [float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11]), float(sys.argv[12]), float(sys.argv[13]), float(sys.argv[14]), float(sys.argv[15]), float(sys.argv[16])]  # Age group proportions
    checkbox = sys.argv[17:] if len(sys.argv) > 17 else []  # Additional options (e.g., isolate, age)
    
    vaccinatedHistoryList = []  # List to track individuals who have been vaccinated

    # Set the proportion of asymptomatic infected cases (global variable)
    p = 0.15

    # Generate population distribution pie chart and age group distribution
    populationPie, ageGroupsDistribution = plotAgeGroup(population, proportion)

    # Choose the appropriate network generation model based on the 'radio' option
    if radio == 'dynamic': 
        GenerateInfectiousUniqueConnections(population, days, seed, ageGroupsDistribution, checkbox)  # Generate dynamic contacts each day
    elif radio == 'same':
        GenerateInfectiousSameConnections(population, days, seed, ageGroupsDistribution, checkbox)  # Generate the same contacts each day
    elif radio == 'complete':
        GenerateInfectiousCompleteConnections(population, days, seed, ageGroupsDistribution)  # Generate a complete contact network

    # Get the daily network data (from 'infectious.csv')
    dailyNetwork = getData('infectious.csv', days)

    # Run the simulation and get the results
    dailyNetwork, infectionPlot, stackBarPlot, infectionRatePlot, degreeVsInfectionPlot, truePositiveRatePlot, overallInfectionRate, dayInfectionRateList, avgDailyConnectionsList = simulate(seed, population, days, affected)

    # Prepare the results in a dictionary
    result = {
        "days": days,  # Number of days in the simulation
        "dailyNetwork": jsonpickle.encode(dailyNetwork),  # Serialize the network data to JSON
        "infectionGraph": infectionPlot.to_json(),  # Serialize the infection plot to JSON
        "populationPie": populationPie.to_json(),  # Serialize the population distribution pie chart to JSON
        "stackBarPlot": stackBarPlot.to_json(),  # Serialize the stacked bar plot to JSON
        "infectionRatePlot": infectionRatePlot.to_json(),  # Serialize the infection rate plot to JSON
        "degreeVsInfectionPlot": degreeVsInfectionPlot.to_json(),
        "truePositiveRatePlot" : truePositiveRatePlot.to_json(),
        "overallInfectionRate": overallInfectionRate,  # Overall infection rate for the entire simulation
        "dayInfectionRateList": dayInfectionRateList,  # List of infection rates for each day
        "avgDailyConnectionsList" : avgDailyConnectionsList
    }

    # Print the results as a JSON string
    # The JSON-encoded result is printed so it can be transferred to the Dash app.
    # Dash will receive this JSON data and use it to update the relevant visualizations and components in the web interface.
    print(json.dumps(result))


if __name__ == '__main__':
    main()
