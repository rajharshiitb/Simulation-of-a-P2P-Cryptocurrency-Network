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
            -all_transaction: <TxnID: 1/0>
            -non_verified_transaction: <TxnID: TxnObject>
            -blockchain datastructure with Genesis block
            -block_tree: maintains block tree in the node
                <BlockID: (BlockObject,chain_length)>
            -tails: maintains leaf blocks, dict type:
                <BlockID: (BlockObject, chain_length)>
            -curr_mining_time: Time at which the node will sucessfully mine a block
        '''
        self.id = id
        self.speed = speed
        self.coins = randrange(21)
        self.peers = None
        self.Tmean_time = Tmean_time
        self.Kmean_time = Kmean_time
        self.all_transaction = {} #max-heap???
        self.non_verfied_transaction = {}
        self.all_block_ids = {}
        self.block_tree = {}
        self.tails={}
        genesis_block = Block(creater_id=id,hash=0,transactions=transactions)
        self.block_tree[genesis_block.getId()] = (genesis_block,1)
        self.tails[genesis_block.getId()] = (genesis_block,1)
        self.curr_mining_time = None
        pass
    def setMiningTime(self,init_mining_time):
        self.curr_mining_time = init_mining_time
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
        Txn_msg = str(self.id)+" pays "+str(toID)+" "+amount+" BTC"
        evenTime = global_time+np.random.exponential(self.Tmean_time,1)
        Txn = Transaction(Txn_msg,evenTime)
        return Event(evenTime,"Txn",self.id,toID,Txn,self.id)
    def receiveTransaction(self,Txn,global_time):
        '''
            Input: 
                Tnx: An object of Transaction
            Eg:
                Tnx at Node A and peers of Node A are: B,D,E

        '''
        events = []
        if Txn.TxnID in self.all_transaction.keys():
            return
        self.non_verfied_transaction[Txn.TxnID] = Txn
        self.all_transaction[Txn.TnxID] = 1
        tokens = Txn.Txn_msg.split()
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
            events.append(Event(global_time+delay,"Txn",fromID,toID,Txn,peer[0]))
        return events
        
    def receiveBlock(self,block,global_time):
        #If block already seen, prevent loop
        if block.id in self.all_block_ids.keys():
            return []
        self.all_block_ids[block.id] = 1
        #Verify all transaction stored in the received block
        under_verification_tnx = {} 
        at = self.block_tree[block.prev_block_hash][0]
        while True:
            Txns = at.transactions
            for Txn in Txns:
                if Txn.fromID!="coinbase":
                    if Txn.fromID in under_verification_tnx.keys():
                        under_verification_tnx[Txn.fromID] -= Txn.coins
                    else:
                        under_verification_tnx[Txn.fromID] = 0-Txn.coins  
                if Txn.toId in under_verification_tnx.keys():
                        under_verification_tnx[Txn.toID] += Txn.coins
                else:
                    under_verification_tnx[Txn.toID] = Txn.coins
            #Break the loop once Genesis Block reached
            if at.prev_block_hash==0:
                break
            at = self.block_tree[at.prev_block_hash][0]
        #Verification Process
        for amount in under_verification_tnx.values():
            if amount<0:
                #Illegal Block
                return self.broadcastBlock(block,global_time)
        #Now that we have verified the block, add the block in the block_tree
        #If prev_block_hash is present in tails then
        #replace the tail with block 
        #else create new branch and add block to the leaf
        if block.prev_block_hash in self.tails.keys():
            self.tails[block.getId()] = (block,self.tails[block.prev_block_hash][1]+1)
            del self.tails[block.prev_block_hash]
        else:
            self.tails[block.getId()] = (block,self.tails[block.prev_block_hash][1]+1)
        #Now broadcast the block to the neighbours 
        return self.broadcastBlock(block,global_time)
        pass
    def generateBlock(self,event):
        #If curr_mine_time != event.eventTime then it means node recerived block before it's own mining can be finished and hence started POW again
        #In this case just return, as this is false mining event
        if self.curr_mining_time!=event.eventTime:
            return []
        #Now that it is confirmed curr Node has sucessfully mined the block
        #We verify the transactions and put in the block and call broadcast it
        
        pass
    def broadcastBlock(self,block,global_time):
        events = []
        fromID = block.creater_id
        toID = "all"
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
            events.append(Event(global_time+delay,"Block",fromID,toID,block,peer[0]))
        #Create new mining_time in both false and true mining event
        self.curr_mining_time = global_time+np.random.exponential(self.Kmean_time,1)
        #create New mining event for the node as per current mining time
        events.append(Event(self.curr_mining_time,"Block",self.id,"all",None,self.id))
        return events
        pass
    
