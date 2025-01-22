class Network:
    """
    A class to represent a network of nodes and provide methods for managing and analyzing connections.

    Methods:
        __init__():
            Initializes an empty dictionary to store nodes by their ids.
        
        addNode(node):
            Adds a node to the network. The node is stored with its id as the key.

        getNode(id):
            Retrieves a node by its id. Returns None if the node is not found.

        getNodes():
            Returns the dictionary of all nodes in the network.

        setNodes(nodes):
            Replaces the current nodes dictionary with a new one.

        getListOfHighestConnections(num):
            Returns a list of the ids of the nodes with the highest number of connections, 
            ensuring the specified number of nodes is returned. 
            Nodes with the next highest number of connections, if specified number is not fulfilled by the highest.

        getSortedNodeListByAge():
            Return a list of node sorted by the oldest age

    Attributes:
        nodes (dict): A dictionary mapping node ids (keys) to node objects (values).
    """

    def __init__(self):
        self.nodes = dict()

    def addNode(self, node):
        self.nodes[node.id] = node

    def getNode(self, id):
        return self.nodes.get(id)
    
    def getNodes(self):
        return self.nodes
        
    def setNodes(self, nodes):
        self.nodes = nodes

    def getListOfHighestConnections(self, num):
        max = 0 
        for node in self.nodes.values(): 
            if len(node.connections) > max:
                max = len(node.connections)
        nodeList = []
        while(len(nodeList)<num): # ensure that there is atleast 3
            for node in self.nodes.values():
                if len(node.connections) == max:
                    nodeList.append(node.id)
            max-=1
        return nodeList
    
    def getSortedNodeListByAge(self):
        return sorted(self.nodes.values(), key=lambda node: node.age, reverse = True)

    
