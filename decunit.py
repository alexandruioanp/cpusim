import gv
import simpy
from pipeline import *
import instruction

class DecUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = None

    def do(self):
        try:
            # while True:
            self.decode()

            if gv.debug_timing:
                print(str(self.env.now) + ": Issued (Decode)", str(self.instr))

            yield self.env.timeout(1)
        except simpy.Interrupt:
            return

    def decode(self):
        self.instr = gv.pipeline.pipe[Stages["DECODE"]]

        if self.instr and self.instr != self.last_instr:
            self.last_instr = self.instr
            self.instr.decode()

            # check for jump
            if self.instr.isUncondBranch:
                gv.fu.jump(self.instr.target)
                self.instr = instruction.getNOP()

            gv.pipeline.pipe[Stages["DECODE"]] = self.instr
            gv.ROB.append(self.instr)
