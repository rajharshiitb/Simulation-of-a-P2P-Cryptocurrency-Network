from node import Node
from parameters import SimulatorParameter
from random import randrange
class InitializeSimulation():
    def __init__(self, path):
        params = SimulatorParameter()
        params.populateParams(path)
        nodes = []
        totalSlow = int(params.z*params.N)
        slowNodes = []
        for i in range(totalSlow):
            peer = randrange(params.N)
            while(peer in slowNodes):
                peer = randrange(params.N)
            slowNodes.append(peer)
        for i in range(params.N):
            if i in slowNodes:
                nodes.append(Node(id=i,speed="slow",peers = peers,Tmean_time=params.Tmean[i],Kmean_time=params.Kmean[i]))
        pass