from block import Block
class Node:
    def __init__(self,id,speed,init_coins,peers,transactions):
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
        self.all_transaction = [] #max-heap???
        self.verfied_transaction = []
        self.block_tree = {}
        genesis_block = Block(creater_id=id,hash=None,chain_length=0,transactions=transactions)
        genesis_block.setId()
        self.block_tree[genesis_block.getId()] = genesis_block
        pass