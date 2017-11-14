import gv
from pipeline import *
import instruction
from collections import deque
import simpy

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = [instruction.getNOP()]
        gv.ROB = deque(maxlen=gv.ROB_entries)

    def do(self):
        # print("WB", self.env.now)
        try:
            # while True:
            instr = gv.pipeline.pipe[Stages["WRITEBACK"]]

            self.writeback()
            if instr:
                self.last_instr = [instr]

            if gv.debug_timing:
                print("W ", self.env.now)

            yield self.env.timeout(1)
        except simpy.Interrupt:
            return

    def writeback(self):
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].opcode == "HALT":
                    # print("OPCODE")
                    pass
                if gv.ROB[0].is_complete:
                    instr = gv.ROB.popleft()
                    if instr != gv.pipeline.pipe[Stages['WRITEBACK']]:
                        # print("BADDDDD")
                        # print(instr, gv.pipeline.pipe[Stages['WRITEBACK']])
                        pass
                    instr.writeback()
                    gv.pipeline.pipe[Stages['WRITEBACK']] = None
                    self.last_instr.append(instr)
                else:
                    break
        except IndexError:
            pass # ROB empty
