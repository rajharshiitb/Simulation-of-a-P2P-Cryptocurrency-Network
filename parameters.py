class SimulatorParameter():
    def __init__(self):
        '''
            -N: Number of peers
            -global_time: Tracks global time
        '''
        self.N = None
        self.global_time = 0
        pass
    def populateParams(self,path):
        '''
            self.N = First Line in file: Number of peers
            self.z = Second Line in file: percent of peers are slow
            self.Tmean = Third Line: contains self.N float numbers which is mean time for generating the Tnx for each peer
            self.Kmean = Fourth Line: contains self.N float numbers which is mean time for generating the Block for each peer
        '''
        