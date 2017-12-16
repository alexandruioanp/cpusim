import collections
import simpy

import gv

Stages = collections.OrderedDict([
        ("FETCH", 0),
        ("DECODE", 1),
        ("RS", 2),])
        # ("WRITEBACK", 3)])
#
# State = {
#     "OK":     0,
#     "STALL":  1,
#     "WHOOPS": 2
# }

rStages = ["FETCH", "DECODE", "RS"]

class Pipeline:
    def __init__(self, env=None):
        self.NUM_STAGES = 2
        self.pipe = [collections.deque()] * self.NUM_STAGES
        self.env = env

    def __str__(self):
        string = ""
        for idx, instr in enumerate(self.pipe):
            string += "("  + list(Stages.keys())[idx][0] + ": " + str(instr) + ") "

        return string

    def get_prev_idx(self, name):
        idx = Stages[name]
        if idx == 0:
            return len(Stages.keys()) - 1
        else:
            return idx - 1

    def get_prev(self, name):
        return gv.stages[self.get_prev_idx(name)]

    def get_next_idx(self, name):
        idx = Stages[name]
        if idx == len(Stages.keys()) - 1:
            return 0
        else:
            return idx + 1

    def get_next(self, name):
        return gv.stages[self.get_next_idx(name)]

    def advance_yield(self):
        self.advance()
        yield self.env.timeout(1)

    def advance(self):
        for i in reversed(range(1, self.NUM_STAGES)):
            if gv.stages[i].status == "READY" and gv.stages[i - 1].status == "READY":
                if gv.debug_timing:
                    if self.pipe[i - 1]:
                        print("moving", [x.asm for x in self.pipe[i - 1]], "from", rStages[i-1], "to", rStages[i])
                    else:
                        print("moving [] from", rStages[i - 1], "to", rStages[i])
                self.pipe[i] = self.pipe[i - 1]
                self.pipe[i - 1] = None
            else:
                break

    def push(self, instr):
        if self.pipe[0]:
            # print("slot 0 not empty", self.pipe[0])
            return 1
        else:
            self.pipe[0] = instr
            return 0

