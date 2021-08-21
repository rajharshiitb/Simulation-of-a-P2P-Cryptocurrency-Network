from block import Block
from transaction import Transaction
from random import randrange
import numpy as np
from event import Event
class Node:
    def __init__(self,id,speed,transactions,Tmean_time,Kmean_time):
        '''
        Intializes the peer with its info
            -peerId
            -speed
            -coins
            -peers: adjacent_peers
            -all_transaction
            -non_verified_transaction
            -verified_transaction
            -blockchain datastructure with Genesis block
            -block_tree: maintains block tree in the node
        '''
        self.id = id
        self.speed = speed
        self.coins = randrange(21)
        self.peers = None
        self.Tmean_time = Tmean_time
        self.Kmean_time = Kmean_time
        self.all_transaction = {} #max-heap???
        self.non_verfied_transaction = {}
        self.verfied_transaction = {}
        self.block_tree = {}
        genesis_block = Block(creater_id=id,hash=0,chain_length=0,transactions=transactions)
        genesis_block.calSummary()
        genesis_block.setId()
        self.block_tree[genesis_block.getId()] = genesis_block
        pass
    def setPeer(self,peer):
        self.peers = peer
    def generateTransaction(self, N,global_time):
        '''
            Take input total number of peers: N
            Returns an object of Event pointing to Tnx type event
        '''
        toID = self.id
        while(toID==self.id):
            toID = randrange(N)
        amount = randrange(1,self.coins+1)
        tnx = str(self.id)+" pays "+str(toID)+" "+amount+" BTC"
        evenTime = global_time+np.random.exponential(self.Tmean_time,1)
        Tnx = Transaction(tnx,evenTime)
        return Event(evenTime,"Tnx",self.id,toID,Tnx,self.id)
    def receiveTransaction(self,Tnx,global_time):
        '''
            Input: 
                Tnx: An object of Transaction
            Eg:
                Tnx at Node A and peers of Node A are: B,D,E

        '''
        events = []
        if Tnx.TxnID in self.all_transaction.keys():
            return
        self.non_verfied_transaction[Tnx.TxnID] = self.all_transaction[Tnx.TnxID] = Tnx
        tokens = Tnx.Txn_msg.split()
        fromID = tokens[0]
        toID = tokens[2]
        for peer in self.peers:
            '''
                peer[0] = node i
                peer[1] = refrence to the node i
                peer[2] = p_ij
            '''
            delay = peer[2]
            c_ij = None
            if self.speed=="fast" and peer[1].speed=="fast":
                c_ij = 100*1e6
            else:
                c_ij = 5*1e6
            delay += (1000/c_ij)*1000 #in milliseconds
            d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
            delay += d_ij
            events.append(Event(global_time+delay,"Tnx",fromID,toID,Tnx,peer[0]))
        return events
        
    def receiveBlock():
        pass
    def generateBlock():
        pass
    def broadcastBlock():
        pass
    
