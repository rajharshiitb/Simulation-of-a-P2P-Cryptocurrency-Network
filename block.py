class Block:
    def __init__(self,bsize,creater_id,hash,chain_length):
        '''
            -max_size = 8*1e6 bits
            -actual_size
            -id: use SHA-256 hash
            -timestamp: creation time
            -creater_id: node which created this
            -prev_block_hash: hash of prev block
            -transactions: (dict or Merkle tree???)
            -length: length of the chain it is part of
        '''
        self.max_size = 8*1e6
        self.actual_size = bsize
        self.timestamp = global_time
        self.creater_id = creater_id
        self.prev_block_hash = hash
        self.transactions = {} #maybe merkel?
        self.length = chain_length+1
        self.id = calSHA()
        pass
    def calSHA():
        pass