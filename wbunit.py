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
        self.writeback()

        if gv.debug_timing:
            print("W ", self.env.now)

        yield self.env.timeout(1)

    def writeback(self):
        self.last_instr = []
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].opcode == "HALT":
                    # print("OPCODE")
                    pass
                if gv.ROB[0].is_complete:
                    instr = gv.ROB.popleft()
                    instr.writeback()
                    self.last_instr.append(instr)
                else:
                    break
        except IndexError:
            pass # ROB empty
