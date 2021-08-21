from transaction import Transaction
from node import Node
from parameters import SimulatorParameter
from random import random, randrange
class InitializeSimulation():
    def __init__(self, path):
        '''
            -params: Create an object of SimulatorParameter which is used to read the simulation parameters from config.txt
            -nodes: contains instance of Node class which is peer in the simulation
        '''
        self.params = SimulatorParameter()
        self.params.populateParams(path)
        self.nodes = []
        #calculate total slow nodes
        totalSlow = int(self.params.z*self.params.N)
        slowNodes = []
        #Create Initial Money/Transaction to each Node
        init_money = [randrange(1,15) for i in range(self.params.N)]
        init_Txn = []
        for id in range(self.params.N):
            #1 init 10 BTC
            Txn_msg = str(id)+" init "+str(init_money[id])+" BTC"
            init_Txn.append(Transaction(Txn_msg,self.params.global_time))
        #Find NodeID of the slow Nodes and save in slowNodes
        for i in range(totalSlow):
            peer = randrange(self.params.N)
            while(peer in slowNodes):
                peer = randrange(self.params.N)
            slowNodes.append(peer) 
        #Create self.params.N nodes in the simulation
        for i in range(self.params.N):
            if i in slowNodes:
                self.nodes.append(Node(id=i,speed="slow",transactions=init_Txn,Tmean_time=self.params.Tmean[i],Kmean_time=self.params.Kmean[i]))
            else:
                self.nodes.append(Node(id=i,speed="fast",transactions=init_Txn,Tmean_time=self.params.Tmean[i],Kmean_time=self.params.Kmean[i]))
        #Now we create the graph
        #First we create the adj matrix and a cell is 1 if it has prbability >=0.3
        adjMatrix = [[int(randrange(0,1)>=0.3) for i in range(self.params.N)] for j in range(self.params.N)]
        #Second, we make sure graph is directed and no self loop
        for i in range(self.params.N):
            for j in range(i,self.params.N):
                if i==j:
                    adjMatrix[i][j] = 0
                    continue
                if adjMatrix[i][j]==1 or adjMatrix[j][i]==1:
                    adjMatrix[i][j] = adjMatrix[j][i] = 1
        #Now we create peer datastructure for each node k
        '''
            node i is adjacent node for node k
            peer[0] = node i
            peer[1] = refrence to the node i
            peer[2] = p_ij
        '''
        for id in range(self.params.N):
            peer = []
            for i in range(self.params.N):
                if adjMatrix[id][i]==1:
                    temp = []
                    temp.append(i)
                    temp.append(self.node[i])
                    temp.append(randrange(10,501))
                peer.append(temp)
            self.nodes[id].setPeer(peer)
        
        pass