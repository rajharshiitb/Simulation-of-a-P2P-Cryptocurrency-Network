import hashlib
class Block:
    def __init__(self,creater_id,hash,chain_length,transactions,global_time):
        '''
            -max_size = 8*1e6 bits
            -actual_size
            -id: use SHA-256 hash
            -timestamp: creation time
            -creater_id: node which created this
            -prev_block_hash: hash of prev block
            -transactions: (dict or Merkle tree???)
            -length: length of the chain it is part of
            -summary
        '''
        self.timestamp = global_time
        self.creater_id = creater_id
        self.prev_block_hash = hash
        self.transactions = transactions #maybe merkel?
        self.summary = None
        self.length = chain_length+1
        self.id = None
        pass
    def calSummary(self):
        '''
        Calculates the hash of the transactions and use that
        as summary
        '''
        concat_transaction = self.transactions[0]
        for trans in self.transactions[1:-1]:
            concat_transaction += (" "+trans)
        result = hashlib.sha256(concat_transaction.encode())
        self.summary = result.hexdigest()
        pass
    def setId(self):
        '''
        Find hash of the block(prev_block_hash||summary)
        and use that as BlockID
        '''
        concat = self.transactions[0]
        for trans in self.transactions[1:-1]:
            concat += (" "+trans)
        concat += (" "+self.summary)
        result = hashlib.sha256(concat.encode())
        self.id = result.hexdigest()
        pass
    def getId(self):
        return self.id