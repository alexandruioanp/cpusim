import gv
from execunit import *
from registerfile import *
from pipeline import *

class Reservierungsstation:
    def __init__(self, env, num_eu):
        self.env = env
        self.num_eu = num_eu
        self.execUnits = []
        self.buffer_size = 16

        for i in range(num_eu):
            self.execUnits.append(ExecUnit(self.env))

    # check if instructions can go ahead, push them to available execution units
    def do(self):

        gv.unit_statuses[Stages["RS"]] = "BUSY"

        for i in range(self.num_eu):
            self.env.process()


        yield self.env.timeout(1)
