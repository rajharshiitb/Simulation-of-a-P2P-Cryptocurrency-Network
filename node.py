from block import Block
from transaction import Transaction
from random import randrange
import numpy as np
from event import Event
class Node:
    def __init__(self,id,speed,init_coins,peers,transactions,mean_time):
        '''
        Intializes the peer with its info
            -peerId
            -speed
            -coins
            -peers: adjacent_peers
            -all_transaction
            -verified_transaction
            -blockchain datastructure with Genesis block
            -block_tree: maintains block tree in the node
        '''
        self.id = id
        self.speed = speed
        self.coins = init_coins
        self.peers = peers
        self.mean_time = mean_time
        self.all_transaction = {} #max-heap???
        self.verfied_transaction = {}
        self.block_tree = {}
        genesis_block = Block(creater_id=id,hash=None,chain_length=0,transactions=transactions)
        genesis_block.setId()
        self.block_tree[genesis_block.getId()] = genesis_block
        pass
    def generateTransaction(self, N):
        '''
            Take input total number of peers: N
            Returns an object of Event pointing to Tnx type event
        '''
        toID = self.id
        while(toID==self.id):
            toID = randrange(N)
        amount = randrange(1,self.coins+1)
        tnx = str(self.id)+" pays "+str(toID)+" "+amount+" BTC"
        Tnx = Transaction(tnx)
        evenTime = np.random.exponential(self.mean_time,1)
        return Event(evenTime,"Tnx",self.id,toID,Tnx)
    def receiveTransaction():
        pass
    def receiveBlock():
        pass
    def generateBlock():
        pass
    def broadcastBlock():
        pass
    
