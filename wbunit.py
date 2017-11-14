import gv
from pipeline import *
import instruction
from collections import deque
import itertools

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = [instruction.getNOP()]
        gv.ROB = deque(maxlen=gv.ROB_entries)

    def do(self):
        # print("WB", self.env.now)
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]

        self.writeback()
        if instr:
            self.last_instr = [instr]

        yield self.env.process(gv.pipeline.get_prev("WRITEBACK").do())

    def writeback(self):
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].is_complete:
                    instr = gv.ROB.popleft()
                    instr.writeback()
                    gv.pipeline.pipe[Stages['WRITEBACK']] = None
                    self.last_instr.append(instr)
                else:
                    break
        except IndexError:
            pass # ROB empty
