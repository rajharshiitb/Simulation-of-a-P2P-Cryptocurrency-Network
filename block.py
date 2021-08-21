import hashlib
from os import stat
class Block:
    def __init__(self,creater_id,hash,chain_length,transactions,timestamp):
        '''
            -id: use SHA-256 hash
            -timestamp: creation time
            -creater_id: node which created this
            -prev_block_hash: hash of prev block
            -transactions: (dict or Merkle tree???)
            -length: length of the chain it is part of
            -summary
        '''
        self.timestamp = timestamp
        self.creater_id = creater_id
        self.prev_block_hash = hash
        self.transactions = transactions #maybe merkel?
        self.summary = None
        self.length = chain_length+1
        self.id = self.setId()
        self.commited_state = None
        pass
    def setState(self,prev_block=None):
        '''
            Contains final financial state of each node so far 
            Two case:
                1. Block is Genesis Block (prev_block_hash==0)
                2. Normal Block
        '''
        if self.prev_block_hash==0:
            state=[0 for i in range(len(self.transactions))]
            for Txn in self.transactions:
                id = Txn.toID
                state[id] = Txn.coins
            self.commited_state = state
        else:
            state = prev_block.commited_state
            for Txn in self.transactions:
                fromID = Txn.fromID
                toID = Txn.toID
                coins = Txn.coins
                if fromID == "mines":
                    state[toID] += coins
                else:
                    state[fromID] += coins
                    state[toID] -= coins
            self.commited_state = state
    def calSummary(self):
        '''
        Calculates the hash of the transactions (Tnx) and use that
        as summary
        '''
        concat_transaction = self.transactions[0].Tnx_msg
        for trans in self.transactions[1:-1]:
            concat_transaction += (" "+trans.Tnx_msg)
        result = hashlib.sha256(concat_transaction.encode())
        self.summary = result.hexdigest()
        pass
    def setId(self):
        '''
        Find hash of the block(prev_block_hash||summary)
        and use that as BlockID
        '''
        self.calSummary()
        concat = self.prev_block_hash
        concat += (" "+self.summary)
        result = hashlib.sha256(concat.encode())
        self.id = result.hexdigest()
        pass
    def getId(self):
        return self.id