class Block:
    def __init__(self):
        '''
            -max_size = 8*1e6 bits
            -actual_size
            -id: use SHA-256 hash
            -timestamp: creation time
            -creater_id: node which created this
            -prev_block_hash: hash of prev block
            -transactions: (list or Merkle tree???)
            -length: length of the chain it is part of
        '''
        pass