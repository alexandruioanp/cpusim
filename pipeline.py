import gv

Stages = {
    "FETCH"     : 0,
    "DECODE"    : 1,
    "EXECUTE"   : 2,
    "WRITEBACK" : 3
}

State = {
    "OK":     0,
    "STALL":  1,
    "WHOOPS": 2
}

class Pipeline:
    def __init__(self):
        self.NUM_STAGES = 4
        self.pipe = [None] * self.NUM_STAGES

    def advance(self):
        if self.pipe == [None] * self.NUM_STAGES:
            return
            # print("no need to advance; pipeline empty")

        if self.pipe[-1]:
            # print("instr", self.pipe[-1], "not retired")
            return 1
        else:
            self.pipe = [None] + self.pipe[:-1]
            return 0

    def push(self, instr):
        if self.pipe[0]:
            print("slot 0 not empty", self.pipe[0])
        else:
            self.pipe[0] = instr

    def stall(self, stage):
        pass
