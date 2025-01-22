from Network import Network

class Node:
    """
    A class to represent a node in a network, storing its properties, connections, 
    and probabilities related to health states in a disease simulation.

    Methods:
        __init__(id, day, age):
            Initializes a node with its ID, day, age, health status probabilities, 
            and an empty list of connections.

        addConnection(connection):
            Adds a new connection to the node's list of connections.

        getConnection(node_to):
            Retrieves a specific connection by the connected node's identifier.

        getConnections():
            Returns the list of all connections associated with the node.

        removeConnection(currentNetworkNodes):
            Removes all connections associated with the node, ensuring that reciprocal 
            connections in other nodes are also removed from the network.

    Attributes:
        id (str): Unique identifier for the node.
        connections (list): List of connected nodes (edges).
        status (str): Current state of the person (e.g., Susceptible, Infectious).
        S (float): Probability of remaining Susceptible the next day.
        P (float): Probability of transitioning to the Presymptomatic state.
        A (float): Probability of transitioning to the Asymptomatic state.
        I (float): Probability of transitioning to the Infectious state.
        R (float): Probability of transitioning to the Recovered state.
        C (float): Total probability of being in the Infectious state.
        age (int): Age of the individual represented by the node.
        day (int): Day of simulation when the node was created.
        avgConnectionByAge (int): Average Connection determined by age group.
        vaccinated (bool): Vaccination status of the person
    """

    def __init__(self, id, day, age):
        self.id = id                   # A name or identifier for the node
        self.connections = list()      # A dict to store edges connected to this node, possible contacts
        self.status = ''               # Starting state of the person
        # probability of transitioning to that state on that day
        self.S = 0                     # Susceptible probability of remaining Susceptible the next day 
        self.P = 0                     # Presymptomatic  
        self.A = 0                     # Asymptomatic
        self.I = 0                     # Infectious
        self.R = 0                     # Recovered
        self.C = 0                     # Total probability of infectious state
        self.age = age
        self.day = day
        self.avgConnectionByAge = 0    # Average Connection by age
        self.vaccinated = False
        
    
    def addConnection(self, connection):
        # Create a new edge and add it to the list of edges
        self.connections.append(connection) # the keys are the NodeTo name so that they are distinct keys

    def getConnection(self, node_to):
        return self.connections.get(node_to)
    
    def getConnections(self):
        return self.connections
    
    def removeConnection(self, currentNetworkNodes):

        for n in self.connections:
            currentNetworkNodes.get(n).getConnections().remove(self.id)   
        self.connections.clear()
        
    
