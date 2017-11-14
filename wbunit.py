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
        yield self.env.timeout(1)
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]

        self.writeback()
        if instr:
            self.last_instr = [instr]

        print("W ", self.env.now)
        # yield self.env.process(gv.pipeline.get_prev("WRITEBACK").do())

    def writeback(self):
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].opcode == "HALT":
                    print("OPCODE")
                    pass
                if gv.ROB[0].is_complete:
                    instr = gv.ROB.popleft()
                    if instr != gv.pipeline.pipe[Stages['WRITEBACK']]:
                        print("BADDDDD")
                        print(instr, gv.pipeline.pipe[Stages['WRITEBACK']])
                    instr.writeback()
                    gv.pipeline.pipe[Stages['WRITEBACK']] = None
                    self.last_instr.append(instr)
                else:
                    break
        except IndexError:
            pass # ROB empty
