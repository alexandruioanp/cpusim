import gv
from pipeline import *
import instruction
from collections import deque
import simpy

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = []
        gv.ROB = deque()
        gv.retired = 0

    def do(self):
        self.writeback()

        if gv.debug_timing:
            print("W ", self.env.now)

        yield self.env.timeout(1)

    def writeback(self):
        self.last_instr = []
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].isExecuted:
                    instr = gv.ROB.popleft()
                    instr.writeback()
                    # print(instr)
                    instr.isRetired = True
                    self.last_instr.append(instr)
                    gv.retired += 1
                else:
                    break
        except IndexError:
            pass # ROB empty
