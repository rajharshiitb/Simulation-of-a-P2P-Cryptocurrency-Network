from transaction import Transaction
from node import Node
from parameters import SimulatorParameter
from random import random, randrange
from event import EventQueue, Event
import numpy as np
class InitializeSimulation():
    def __init__(self, path):
        '''
            -TODO:
                1. Create initial Tnx Events
                2. Create initial Block_mining Events and set the curr_mining_time of each block
            -params: Create an object of SimulatorParameter which is used to read the simulation parameters from config.txt
            -nodes: contains instance of Node class which is peer in the simulation
        '''
        self.params = SimulatorParameter()
        self.params.populateParams(path)
        self.nodes = []
        self.global_time = 0
        self.q = EventQueue()
        #calculate total slow nodes
        totalSlow = int(self.params.z*(self.params.N)/100)
        slowNodes = []
        #Create Initial Money/Transaction to each Node
        init_money = [randrange(1,15) for i in range(self.params.N)]
        init_Txn = []
        for id in range(self.params.N):
            #1 init 10 BTC
            Txn_msg = str(id)+" init "+str(init_money[id])+" BTC"
            init_Txn.append(Transaction(Txn_msg,self.global_time))
        #Find NodeID of the slow Nodes and save in slowNodes
        for i in range(totalSlow):
            peer = randrange(self.params.N)
            while(peer in slowNodes):
                peer = randrange(self.params.N)
            slowNodes.append(peer) 
        #Create self.params.N nodes in the simulation
        for i in range(self.params.N):
            if i in slowNodes:
                self.nodes.append(Node(id=i,speed="slow",transactions=init_Txn,Tmean_time=self.params.Tmean[i],Kmean_time=self.params.Kmean[i],global_time = self.global_time))
            else:
                self.nodes.append(Node(id=i,speed="fast",transactions=init_Txn,Tmean_time=self.params.Tmean[i],Kmean_time=self.params.Kmean[i],global_time = self.global_time))
        #Now we create the graph
        #First we create the adj matrix and a cell is 1 if it has prbability >=0.3
        adjMatrix = [[np.random.uniform(0,1) for i in range(self.params.N)] for j in range(self.params.N)]
        #Second, we make sure graph is directed and no self loop
        for i in range(self.params.N):
            for j in range(i,self.params.N):
                if i==j:
                    adjMatrix[i][j] = 0
                    continue
                if adjMatrix[i][j]>=0.3 or adjMatrix[j][i]>=0.3:
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
                    temp.append(self.nodes[i])
                    temp.append(randrange(10,501))
                    peer.append(temp)
            self.nodes[id].setPeer(peer)
        #Create Initial Tnx Event for each Node
        for id in range(self.params.N):
            self.q.push(self.nodes[id].generateTransaction(self.params.N,self.global_time))
        #create initial Block Event
        for id in range(self.params.N):
            mining_time = self.global_time+np.random.exponential(self.nodes[id].Kmean_time,1)
            #create New mining event for the node as per current mining time
            self.q.push(Event(mining_time,"Block",id,"all",None,id))
            self.nodes[id].setMiningTime(mining_time)
        pass