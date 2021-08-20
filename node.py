class Node:
    def __init__(self,id,speed,init_coins,peers):
        '''
        Intializes the peer with its info
            -peerId
            -speed
            -coins
            -adjacent_peers
            -all_transaction
            -verified_transaction
            -blockchain datastructure with Genesis block
            
        '''
        self.id = id
        self.speed = speed
        pass