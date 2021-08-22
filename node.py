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
            -all_transaction: <TxnID: Txn object>
            -non_verified_transaction
            -verified_transaction
            -blockchain datastructure with Genesis block
            -block_tree: maintains block tree in the node
                <BlockID: (BlockObject,chain_length)>
            -tails: maintains leaf blocks, dict type:
                <BlockID: (BlockObject, chain_length)>
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
        self.tails={}
        genesis_block = Block(creater_id=id,hash=0,transactions=transactions)
        self.block_tree[genesis_block.getId()] = (genesis_block,1)
        self.tails[genesis_block.getId()] = (genesis_block,1)
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
        self.non_verfied_transaction[Txn.TxnID] = self.all_transaction[Txn.TnxID] = Txn
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
                return self.broadcastBlock()
        #Now that we have verified the block, add the block in the block_tree
        #If prev_block_hash is present in tails then
        #replace the tail with block 
        #else create new branch and add block to the leaf
        if block.prev_block_hash in self.tails.keys():
            self.tails[block.getId()] = (block,self.tails[block.prev_block_hash][1]+1)
            del self.tails[block.prev_block_hash]
        else:
            self.tails[block.getId()] = (block,self.tails[block.prev_block_hash][1]+1)

        pass
    def generateBlock(self):
        pass
    def broadcastBlock():
        pass
    
