class Node:
    def __init__(self,id,speed,init_coins,peers):
        '''
        Intializes the peer with its info
            -peerId
            -speed
            -coins
            -peers: adjacent_peers
            -all_transaction
            -verified_transaction
            -blockchain datastructure with Genesis block

        '''
        self.id = id
        self.speed = speed
        self.coins = init_coins
        self.peers = peers
        self.all_transaction = [] #max-heap???
        self.verfied_transaction = []
        #ToDo
        '''
        Initialize Genesis Block
        '''
        pass