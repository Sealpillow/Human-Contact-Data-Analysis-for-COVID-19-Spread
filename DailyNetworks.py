class DailyNetworks:
    """
    A class to manage and compare networks on a daily basis.

    Methods:
        __init__():
            Initializes an empty dictionary to store networks by day.
        
        addNetworkByDay(day, newNetwork):
            Adds a network for a specific day.

        getNetworkByDay(day):
            Retrieves the network for a given day. Returns None if the day is not found.

    Attributes:
        networks (dict): A dictionary mapping days (keys) to their respective networks (values).
    """
    def __init__(self):
        self.networks = dict()
        self.totalConnections = 0

    def addNetworkByDay(self, day, newNetwork):
        self.networks[day] = newNetwork

    def getNetworkByDay(self, day):
        return self.networks.get(day)
    
