from enum import Enum

import global_vars

Stages = {
    "FETCH"     : 0,
    "DECODE"    : 1,
    "EXECUTE"   : 2,
    "WRITEBACK" : 3
}

class State(Enum):
    OK     = 0
    STALL  = 1
    WHOOPS = 2

class Pipeline:
    def __init__(self):
        self.NUM_STAGES = 4
        self.pipe = [None] * self.NUM_STAGES

    def advance(self):
        if self.pipe[-1]:
            print("instr", self.pipe[-1], "not retired")
            return 1
        else:
            self.pipe = [None] + self.pipe[:-1]
            return 0

    def push(self, instr):
        a = self.advance()

        if a == 0:
            if self.pipe[0]:
                print("slot 0 not empty", self.pipe[0])
            else:
                self.pipe[0] = instr
        else:
            print("could not advance pipeline")
