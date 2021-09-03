from block import Block
from transaction import Transaction
from random import randrange
import numpy as np
from event import Event
from queue import Queue
from graphviz import Graph
class Node:
    def __init__(self,id,speed,transactions,Tmean_time,Kmean_time,global_time):
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
        self.genesis_block = Block(creater_id=id,hash=0,transactions=transactions,timestamp=global_time)
        self.block_tree[self.genesis_block.id] = (self.genesis_block,1)
        self.tails[self.genesis_block.id] = (self.genesis_block,1)
        self.curr_mining_time = None
        self.longest_chain = (self.genesis_block,1)
        self.non_verified_blocks = {}
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
        amount = randrange(0,self.coins+1)
        Txn_msg = str(self.id)+" pays "+str(toID)+" "+str(amount)+" BTC"
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
            return events
        self.non_verfied_transaction[Txn.TxnID] = Txn
        self.all_transaction[Txn.TxnID] = 1
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

    def verify(self, block,global_time):
        under_verification_tnx = {} 
        events = []
        at = block
        while True:
            Txns = at.transactions
            for Txn in Txns:
                if Txn.fromID!="coinbase":
                    if Txn.fromID in under_verification_tnx.keys():
                        under_verification_tnx[Txn.fromID] -= Txn.coins
                    else:
                        under_verification_tnx[Txn.fromID] = 0-Txn.coins  
                if Txn.toID in under_verification_tnx.keys():
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
                return ([],False)
        #delete all txns that are present in the block from non_verified_Txn
        for txn in block.transactions:
            if txn.TxnID in self.non_verfied_transaction.keys():
                del self.non_verfied_transaction[txn.TxnID]
        #Now that we have verified the block, add the block in the block_tree
        self.block_tree[block.id] = (block, self.block_tree[block.prev_block_hash][1]+1)
        #If prev_block_hash is present in tails then
        #replace the tail with block 
        #else create new branch and add block to the leaf
        self.tails[block.id] = (block,self.block_tree[block.prev_block_hash][1]+1)
        if block.prev_block_hash in self.tails.keys():
            del self.tails[block.prev_block_hash]
        #If longest_chain has been changed by adding current block
        if self.longest_chain[1]<self.tails[block.id][1]:
            #Create new mining_time in both false and true mining event
            self.curr_mining_time = global_time+np.random.exponential(self.Kmean_time,1)
            #create New mining event for the node as per current mining time
            events.append(Event(self.curr_mining_time,"Block",self.id,"all",None,self.id))
            self.longest_chain = self.tails[block.id]
        #Now broadcast the block to the neighbours 
        return (events,True)

    def receiveBlock(self,block,global_time):
        '''
        Issue: Parent not found
        Too many not added in tree bcz parent not there
        When parent received and parent itself is not valid
            Discard all the children
        when parent is valid
            Then recursively find all child blocks which are valid
        Type of storage:
            1. block_tree: dict <block_id: <block_obj, len>>
            2. non_verified_blocks: dict <block.prev_block_hash: dict <block_id: block_obj>>
                searching time O(1)
                 -g
                a-h-k
                 -i
                K came
                 
                h came
                {a_hash: h_obj}
        '''
        #If block already seen, prevent loop
        if block.id in self.all_block_ids.keys():
            return []
        self.all_block_ids[block.id] = 1
        #Check if parent of the block is in the block tree or not
        parent_hash = block.prev_block_hash
        if parent_hash not in self.block_tree.keys():
            if parent_hash not in self.non_verified_blocks.keys():
                self.non_verified_blocks[parent_hash] = {}
            self.non_verified_blocks[parent_hash][block.id] = block
            #return empty event list
            return self.broadcastBlock(block,global_time,[])
        #Now if the parent of the block present in the block_tree then recursively verify all
        #the children too
        q = Queue()
        q.put(block)
        events = []
        while(not q.empty()):
            curr_block = q.get()
            result = self.verify(curr_block,global_time)
            if result[1]:
                #Means block was legal
                events.extend(result[0])
                if curr_block.id in self.non_verified_blocks.keys():
                    for child_id in self.non_verified_blocks[curr_block.id].keys():
                        q.put(self.non_verified_blocks[curr_block.id][child_id])
                    del self.non_verified_blocks[curr_block.id]
        return self.broadcastBlock(block,global_time,events)
    def generateBlock(self,event,global_time):
        #If curr_mine_time != event.eventTime then it means node recerived block before it's own mining can be finished and hence started POW again
        #In this case just return, as this is false mining event
        if self.curr_mining_time!=event.eventTime:
            return []
        events = []
        #Genrate New block_mine event
        #Create new mining_time in both false and true mining event
        self.curr_mining_time = global_time+np.random.exponential(self.Kmean_time,1)
        #create New mining event for the node as per current mining time
        events.append(Event(self.curr_mining_time,"Block",self.id,"all",None,self.id))
        #Now that it is confirmed curr Node has sucessfully mined the block
        #We verify the transactions and put in the block and call broadcast it
        verified_Txns = []
        #calculate the Transaction state till last block in the longest chain
        Txn_state = {} 
        at = self.longest_chain[0]
        while True:
            Txns = at.transactions
            for Txn in Txns:
                if Txn.fromID!="coinbase":
                    if Txn.fromID in Txn_state.keys():
                        Txn_state[Txn.fromID] -= Txn.coins
                    else:
                        Txn_state[Txn.fromID] = 0-Txn.coins  
                if Txn.toID in Txn_state.keys():
                        Txn_state[Txn.toID] += Txn.coins
                else:
                    Txn_state[Txn.toID] = Txn.coins
            #Break the loop once Genesis Block reached
            if at.prev_block_hash==0:
                break
            at = self.block_tree[at.prev_block_hash][0]
        count = 0
        #Find valid transactions to put inside the block
        TxnIDs = self.non_verfied_transaction.keys()
        size = len(self.non_verfied_transaction)
        valid = 0
        for TxnID in TxnIDs:
            count += 1
            Txn = self.non_verfied_transaction[TxnID]
            if Txn.fromID != "coinbase":
                if Txn_state[Txn.fromID] < Txn.coins:
                    continue
                Txn_state[Txn.fromID] -= Txn.coins
            Txn_state[Txn.toID] += Txn.coins
            verified_Txns.append(Txn)
            valid +=1
            if  count>=size or valid>=1000:
                break
        for Txn in verified_Txns:
            del self.non_verfied_transaction[Txn.TxnID]
        verified_Txns.append(Transaction(str(self.id)+" mines 50 BTC",global_time))
        parent = self.longest_chain[0]
        lon = self.longest_chain[1]
        block = Block(self.id,parent.id,verified_Txns,event.eventTime)
        self.block_tree[block.id] = (block, lon+1)
        self.longest_chain = (block, lon+1)
        self.all_block_ids[block.id] = 1
        return self.broadcastBlock(block,global_time,events)
    def broadcastBlock(self,block,global_time,events):
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
            delay += (1000000/c_ij)*1000 #in milliseconds
            d_ij = np.random.exponential(((96*1000)/c_ij),1)*1000 #in milliseconds
            delay += d_ij
            events.append(Event(global_time+delay,"Block",fromID,toID,block,peer[0]))
        return events    
    
    def visualize(self):
        tree = {}
        for block_id in self.block_tree.keys():
            parent_hash = self.block_tree[block_id][0].prev_block_hash
            if parent_hash not in tree.keys():
                tree[parent_hash] = {}
            tree[parent_hash][block_id] = self.block_tree[block_id][0]
        queue = Queue()
        queue.put(0)
        graph = Graph('parent',filename=str(self.id))
        graph.attr(rankdir='LR',splines='line')
        count = 0
        hash = {}
        while not queue.empty():
            size = queue.qsize()
            temp = Graph('child')
            while size>0:
                parent_hash = queue.get()
                for child_id in tree[parent_hash].keys():
                    temp.node(str(count))
                    hash[child_id] = str(count)
                    if parent_hash!=0:
                        graph.edge(str(count),hash[tree[parent_hash][child_id].prev_block_hash])
                    count += 1
                    if child_id in tree.keys():
                        queue.put(child_id)
                size -= 1
            graph.subgraph(temp)
        graph.view()



