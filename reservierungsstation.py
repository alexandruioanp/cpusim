import gv
from execunit import *
from registerfile import *
from pipeline import *
from collections import deque

class Reservierungsstation:
    def __init__(self, env, num_eu):
        self.env = env
        self.num_eu = num_eu
        self.execUnits = []
        self.buffer_size = 16
        self.shelved_instr = deque(maxlen=self.buffer_size)
        self.status = "READY"

        for i in range(num_eu):
            self.execUnits.append(ExecUnit(self.env, i))

    def push(self, instr):
        if len(self.shelved_instr) < self.buffer_size: # can shelve more
            self.shelved_instr.append(instr)
            return 0
        else:
            self.status = "BUSY"
            return 1

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        for eu in self.execUnits:
            if self.shelved_instr:
                if eu.status == "READY": # distribute instruction
                    self.env.process(eu.do(self.shelved_instr.popleft()))
                    pass
            else:
                break

        yield self.env.timeout(1)
