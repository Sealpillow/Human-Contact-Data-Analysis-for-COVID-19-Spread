import numpy as np
import os 
import math
from scipy.integrate import quad
from plotGraph import plotResult, plotStackBar, plotAgeGroup
from scipy.stats import lognorm, norm
from Network import Network
from Node import Node
from DailyNetworks import DailyNetworks
from GenerateConnectionsCsv import GenerateInfectiousUniqueConnections, GenerateInfectiousSameConnections, GenerateInfectiousCompleteConnections,GenerateInfectiousModelConnections
import json
import sys
import jsonpickle
import csv


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
                newNode1 = Node(person1, day, age1)  # create Node1
                newNode1.avgConnectionByAge = getConnections(newNode1.age)
                currNetwork.addNode(newNode1)            # add the new node
            else:
                newNode1 = currNetwork.getNode(person1)

                
            if person2 not in currNetwork.getNodes().keys():    
                newNode2 = Node(person2, day, age2)  # create Node2
                newNode2.avgConnectionByAge = getConnections(newNode2.age)
                currNetwork.addNode(newNode2)            # add the new node 
            else:
                newNode2 = currNetwork.getNode(person2)

            newNode1.addConnection(person2)
            newNode2.addConnection(person1)

    return dailyNetworks
    

def getConnections(age):
    if age < 25:
        return 0.0856    
    elif 25 <= age <= 44:
        return 0.226  
    elif 45 <= age <= 64:
        return 0.227
    elif 65 <= age <= 74:
        return 0.15
    else:                 
        return 0.128 


def update_network(day):   # Check the current day network if any one is in infected state-> isolate -> remove the person's connections
    global dailyNetwork
    currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()     
    for person in currentNetworkNodes.values():  
        if person.status == 'I' and len(person.getConnections()) > 0: # if current person status is infectious, isolate the person from the rest, break all edges (from and to that node)
            person.removeConnection(currentNetworkNodes)



# Compute the CDFs F_P(d), F_I(d), and F_A(d)
def F_P(d):
    meanP = 1.43                                            # Mean of the underlying normal distribution
    stdP = 0.66                                             # Standard deviation of the underlying normal distribution 
    return lognorm(s=meanP, scale=np.exp(stdP)).cdf(d)
    #return lognorm.cdf(np.arange(1,41)/4.17,s=0.66)[d]

def F_I(d):
    meanI = 8.8                                             # Mean
    stdI = 3.88                                             # Standard deviation
    return norm(loc=meanI, scale=stdI).cdf(d) #
    #return norm.cdf((np.arange(1,41)-8.82)/3.88)[d]

def F_A(d):
    meanA = 20.0                                            # Mean
    stdA = 5.0                                              # Standard deviation
    return norm(loc=meanA, scale=stdA).cdf(d) 
    #return norm.cdf((np.arange(1,41)-20)/5)[d]

def Beta(day, person):
    global dailyNetwork, population, p, checkbox, overallReproNum
    reproNum = overallReproNum# Basic reproduction number
    meanA = 20.0              # average time of the virus carried by infected individuals in state A
    meanP = 1.43              # average time of the virus carried by infected individuals in state P
    meanI = 8.8               # average time of the virus carried by infected individuals in state I
    sigma_P = 0.66            # standard deviation of the virus carried by infected individuals in state P
    overallInfectRate = 13.4
    total_connections = 0 
    for person in dailyNetwork.getNetworkByDay(day).getNodes().values():
        total_connections += len(person.getConnections())  # count the total number of connections in then network -> edges
    avgNumNeighNet_k = total_connections/population
    avgtimesusceptible_lambda = p * meanA + (1 - p) * (math.exp(meanP + (sigma_P**2) / 2) + meanI)
    
    # Report on reduction in infection rate
    # https://www.sciencedirect.com/science/article/pii/S0140673621004487?pes=vor&utm_source=tfo&getft_integrator=tfo
    if 'vaccination' in checkbox:
        if 1 <= day - interventionDay <=14:
            reproNum *= (1 - 0.3)
        elif day - interventionDay >= 15:
            reproNum *= (1 - 0.75)
    if 'age' in checkbox:
        reproNum *= person.avgConnectionByAge/overallInfectRate        
    

    beta = reproNum / (avgtimesusceptible_lambda * avgNumNeighNet_k)
    # beta: 0.01989534303906822
    return beta

def F(t, j, beta):
    #  from the report 
    #  Ci(t) = Pi(t) + Ii(t) + Ai(t)
    #  F(t,j,β) = Cj(t)·β
    global dailyNetwork
    return dailyNetwork.getNetworkByDay(t).getNode(j).C * beta

def getLatestPeriod(status, personID, day):
    global dailyNetwork

    count = 0

    for d in range(day,0,-1):
        xStatus = dailyNetwork.getNetworkByDay(d).getNode(personID).status
        if xStatus != status:
            return count
        else: 
            count+=1
    return count


def sumProb(personID, day, state):
    global dailyNetwork, checkbox
    prob = 0
    for d in range(day,0,-1):
        node = dailyNetwork.getNetworkByDay(d).getNode(personID)
        if state == 'P':
            prob += node.P
        elif state == 'A':
            prob += node.A
        elif state == 'I':
            prob += node.I
    return prob
# update probabilities for the next day 
def update_probabilities(day):
    #print(day)
    global dailyNetwork, p, checkbox
    currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()
    for person in currentNetworkNodes.values():                                                 # iterate every single person's status on that day
        personNextDay = dailyNetwork.getNetworkByDay(day+1).getNode(person.id)
        if person.status == 'S':                                                               # if person in S state update prob accordingly
            # this is solely based on connections
            connections = person.getConnections()
            NotInfectedByNeighbourProb = np.prod([(1 - F(day, connection, Beta(day, person))) for connection in connections])
            infectionProb = (1 - NotInfectedByNeighbourProb) 
            personNextDay.P = person.S * (1-p) * infectionProb                          
            personNextDay.A = person.S * p * infectionProb
            personNextDay.S = 1 - personNextDay.P - personNextDay.A
            # old : personNextDay.S = person.S * np.prod([(1 - F(day, connection, Beta(day))) for connection in connections]) 
            # new
            

        elif person.status == 'P':                                                           # if person in P state, update prob accordingly
            d = getLatestPeriod('P', person.id, day)                                         # get latest period where person is in P state
            '''if 'age' in checkbox:
                personNextDay.I = (sumProb(person.id, day, 'P'))  * (F_P(d) - F_P(d-1)) / (1 - F_P(d-1)) * 0.29
            else:'''
            personNextDay.I = (sumProb(person.id, day, 'P',))  * (F_P(d) - F_P(d-1)) / (1 - F_P(d-1)) #* 0.29
            personNextDay.P = 1-personNextDay.I

        elif person.status == 'I':                                                           # if person in I state, update prob accordingly
            d = getLatestPeriod('I', person.id, day)                                         # get latest period where person is in I state
            '''if 'age' in checkbox:
                personNextDay.R = person.R + sumProb(person.id, day, 'I') * (F_I(d) - F_I(d-1)) / (1 - F_I(d-1)) * 0.04
            else:'''
            personNextDay.R = person.R + sumProb(person.id, day, 'I') * (F_I(d) - F_I(d-1)) / (1 - F_I(d-1))#  * 0.04
            personNextDay.I = 1 - personNextDay.R
        elif person.status == 'A':                                                           # if person in A state, update prob accordingly
            d = getLatestPeriod('A', person.id, day)                                         # get latest period where person is in A state
            '''if 'age' in checkbox:
                personNextDay.R = person.R + sumProb(person.id, day, 'A') * (F_A(d) - F_A(d-1)) / (1 - F_A(d-1)) * 0.04
            else:'''
            personNextDay.R = person.R + sumProb(person.id, day, 'A') * (F_A(d) - F_A(d-1)) / (1 - F_A(d-1))#* 0.04
            personNextDay.A = 1 - personNextDay.R
        personNextDay.C = personNextDay.P + personNextDay.I + personNextDay.A 




def update_status(day, rng):
    global dailyNetwork
    currentNetworkNodes = dailyNetwork.getNetworkByDay(day).getNodes()
    for person in currentNetworkNodes.values():                                  # iterate every single person's status on that day
        personNextDay = dailyNetwork.getNetworkByDay(day+1).getNode(person.id)
        rand = rng.random()                                                                   # rolling probability
        if person.status == 'S':                                                                 # Person at Susceptible state 
            if rand < personNextDay.P:                                                           # Probability that Exposed becomes Presymptomatic
                personNextDay.status = 'P'   
                personNextDay.P = 1                                                              # Set probability of Presymptomatic for the next day to 1 since that person will be Presymptomatic for the next day
                personNextDay.S = 0                                                              # Not possible to reverse state, hence P = 0
                personNextDay.A = 0                                                              # Not possible to reverse state, hence A = 0 
            elif rand < personNextDay.P + personNextDay.A:                                       # Probability that Exposed becomes Presymptomatic
                personNextDay.status = 'A'   
                personNextDay.P = 0                                                              # Not possible to reverse state, hence P = 0
                personNextDay.S = 0                                                              # Not possible to reverse state, hence S = 0
                personNextDay.A = 1                                                              # Set probability of Presymptomatic for the next day to 1 since that person will be Presymptomatic for the next day
            else:
                personNextDay.status = 'S'         
        elif person.status == 'P':                                                               # Person at Presymptomatic state 
            # probabilities are checked correctly without giving one priority over the other.                                                                   
            if rand < personNextDay.I:                                                           # Probability that Presymptomatic becomes Infectious -> # ( 0.2 < x < 0.2 + 0.4 )
                personNextDay.status = 'I'
                personNextDay.I = 1                                                              # Set probability of Infectious for the next day to 1 since that person will be Infectious for the next day
                personNextDay.P = 0                                                              # Not possible to reverse state, hence P = 0
            else:
                personNextDay.status = 'P'
        elif person.status == 'I':                                                               # Person at Infectious state 
            if rand < personNextDay.R:                                                           # Probability that Infectious becomes Recovered
                personNextDay.status = 'R'
                personNextDay.R = 1                                                              # Set probability of Recovered for the next day to 1 since that person will be Recovered for the next day
                personNextDay.I = 0                                                              # Not possible to reverse state, hence I = 0
            else:
                personNextDay.status = 'I'
        elif person.status == 'A':                                                               # Person at Asymptomatic state 
            if rand < personNextDay.R:                                                           # Probability that Asymptomatic becomes Recovered
                personNextDay.status = 'R'
                personNextDay.R = 1                                                              # Set probability of Recovered for the next day to 1 since that person will be Recovered for the next day
                personNextDay.A = 0                                                              # Not possible to reverse state, hence A = 0            
            else:
                personNextDay.status = 'A'
        else:         # should i do this? Recovered patients stay in recoved status or for Recovered patients, or will transition to a Susceptible state the next day, as they may get exposed again
            personNextDay.status = 'R'   
            personNextDay.R = 1 


def simulate(seed, population, days, randomNumPeople):
    global dailyNetwork, p, checkbox
    rng = np.random.default_rng(seed)
    # ramdomize infected people

    # Set infected people in the grid
    initialNetwork = dailyNetwork.getNetworkByDay(1)

    # choose numSpreaders(5) random person from population that has the highest connections
    numbers = initialNetwork.getListOfHighestConnections(randomNumPeople)
    originSpreaders = rng.choice(numbers, size=randomNumPeople, replace=False)
    for id in range(1, population+1):
        node = initialNetwork.getNode(id)
        if id in originSpreaders: # if node are the origin spreaders
            rand = rng.random()
            if rand < p:   
                node.status = 'A'
                node.A = 1
            else:
                node.status = 'P'
                node.P = 1
        else:
            node.status = 'S' 
            node.S = 1
    
    
    # print('Setup complete')

    # Simulation
    susceptible_counts = []
    presymptomatic_counts = []
    asymptomatic_counts = []
    infected_counts = []
    recovered_counts = []

    for day in range(1, days+1):
        # print(f"Day num: {day}")
        if day < days: # update new probability till the day before the last day
            if 'isolate' in checkbox:
                update_network(day)  # Self-isolate
            update_probabilities(day)
            update_status(day, rng) # add this back when E[person][day] is setup
        currentNodes = dailyNetwork.getNetworkByDay(day).getNodes()    
        susceptible_counts.append(sum(1 for person in currentNodes.values() if person.status == 'S'))
        presymptomatic_counts.append(sum(1 for person in currentNodes.values()  if person.status == 'P'))
        asymptomatic_counts.append(sum(1 for person in currentNodes.values()  if person.status == 'A'))
        infected_counts.append(sum(1 for person in currentNodes.values()  if person.status == 'I'))
        recovered_counts.append(sum(1 for person in currentNodes.values() if person.status == 'R'))
        with open("progress.txt", "w") as f:
            f.write(str(round(day/days*100)))
    # plotGraph(days,susceptible_counts,presymptomatic_counts,asymptomatic_counts,infected_counts,recovered_counts)
    infectionPlot = plotResult(days,susceptible_counts,presymptomatic_counts,asymptomatic_counts,infected_counts,recovered_counts)
    stackBarPlot = plotStackBar(days,susceptible_counts,presymptomatic_counts,asymptomatic_counts,infected_counts,recovered_counts)
    return dailyNetwork, infectionPlot, stackBarPlot

def main():
    global dailyNetwork
    global population
    global days
    global seed
    global overallReproNum
    global p 
    global interventionDay
    global checkbox
    # Parameters

    '''
    sys.argv = [
    'python',                # Not typically part of sys.argv when executing the script itself
    'path_to_template.py',   # Template script path (template_path)
    '123456',                # seed (str(seed))
    '410',                   # population (str(population))
    '100',                   # days (str(days))
    '5',                     # affected (str(affected))
    'same',                  # radio (str(radio))
    '60',                    # proportionList[0]
    '25',                    # proportionList[1]
    '12',                    # proportionList[2]
    '2',                     # proportionList[3]
    '1',                     # proportionList[4]
    'isolate',               # checkbox[0]
    'age',                   # checkbox[1]
    ]
    '''
    '''
    population = 410
    days = 100
    affected = 5
    seed = 12345
    radio = 'same'
    checkbox = ['age']
    proportion = [20,20,20,20,20]
    '''
    seed = int(sys.argv[1]) # to have a fix seed for reproducibility
    overallReproNum = float(sys.argv[2])
    population = int(sys.argv[3])
    days = int(sys.argv[4])
    affected = int(sys.argv[5])
    interventionDay = int(sys.argv[6])
    radio = sys.argv[7]
    proportion = [int(sys.argv[8]),int(sys.argv[9]),int(sys.argv[10]),int(sys.argv[11]),int(sys.argv[12])]
    checkbox = sys.argv[13:] if len(sys.argv) > 13 else []
    
    # Convert the comma-separated string back to a list
    with open("progress.txt", "w") as f:
        f.write(str(0))

    #min_connections_per_person = 4
    #max_repeated_connections = 2
    avgDeg = 16.49
    p = 0.15                              # proportion of asymptomatic infected cases
    connectionsPerDay = population*avgDeg # prob can set based on optimal connections
    populationPie, ageGroupsDistribution = plotAgeGroup(population, proportion)  
    if radio == 'unique': 
        GenerateInfectiousUniqueConnections(population, days, seed, ageGroupsDistribution) # uncomment it if u want to continuous generate new connections
    elif radio == 'same':
        GenerateInfectiousSameConnections(population, days, seed, ageGroupsDistribution) # uncomment it if u want to continuous generate new connections
    elif radio == 'complete':
        GenerateInfectiousCompleteConnections(population, days, seed, ageGroupsDistribution)
    elif radio == 'model':
        GenerateInfectiousModelConnections(population, days, seed, ageGroupsDistribution)
      
    dailyNetwork = getData('infectious.csv', days)
    dailyNetwork, infectionPlot, stackBarPlot = simulate(seed, population, days, affected)
    result = {
        "days": days,
        "dailyNetwork": jsonpickle.encode(dailyNetwork),  # jsonpickle is a Python library for serialization and deserialization of complex Python objects to and from JSON.
        "infectionGraph": infectionPlot.to_json(), # converts the figure into a JSON string that can be transmitted or stored
        "populationPie" : populationPie.to_json(),
        "stackBarPlot" : stackBarPlot.to_json()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
