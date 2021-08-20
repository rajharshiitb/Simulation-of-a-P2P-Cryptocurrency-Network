from parameters import SimulatorParameter
class InitializeSimulation():
    def __init__(self, path):
        params = SimulatorParameter()
        params.populateParams(path)
        pass