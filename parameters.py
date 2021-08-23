class SimulatorParameter():
    def __init__(self):
        '''
            -N: Number of peers
            -global_time: Tracks global time
        '''
        self.N = None
        self.z = None
        self.Tmean = []
        self.Kmean = []
        pass
    def populateParams(self,path):
        '''
            self.N = First Line in file: Number of peers
            self.z = Second Line in file: percent of peers are slow
            self.Tmean = Third Line: contains self.N float numbers which is mean time for generating the Tnx for each peer
            self.Kmean = Fourth Line: contains self.N float numbers which is mean time for generating the Block for each peer
        '''
        file = open(path,"r")
        count = 1
        for line in file:
            if count==1:
                self.N = int(line)
                count +=1
                continue
            elif count==2:
                self.z = int(line)
                count +=1
                continue
            elif count==3:
                mean = line.split()
                self.Tmean = [int(x) for x in mean]
                count +=1
                continue
            elif count==4:
                mean = line.split()
                self.Kmean = [int(x) for x in mean]
                break
        pass
            