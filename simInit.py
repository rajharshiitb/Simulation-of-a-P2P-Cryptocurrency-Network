from node import Node
from parameters import SimulatorParameter
from random import random, randrange
class InitializeSimulation():
    def __init__(self, path):
        params = SimulatorParameter()
        params.populateParams(path)
        #Intialize Nodes and create graph
        nodes = []
        totalSlow = int(params.z*params.N)
        slowNodes = []
        for i in range(totalSlow):
            peer = randrange(params.N)
            while(peer in slowNodes):
                peer = randrange(params.N)
            slowNodes.append(peer)
        #TODO:
        #make this graph undirected
        #Done
        for i in range(params.N):
            node_set = set([i for i in range(params.N)])
            node_set.discard(i)
            peer = []
            neighbours = randrange(1,params.N)
            for i in range(neighbours):
                peer.append(random.choice(node_set))
                node_set.discard(peer[-1])
            if i in slowNodes:
                nodes.append(Node(id=i,speed="slow",peers = peer,Tmean_time=params.Tmean[i],Kmean_time=params.Kmean[i]))
            else:
                nodes.append(Node(id=i,speed="fast",peers = peer,Tmean_time=params.Tmean[i],Kmean_time=params.Kmean[i]))
        
        pass