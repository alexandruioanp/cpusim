import gv
from pipeline import *
import instruction

class DecUnit:
    def __init__(self, env):
        self.env = env

    def do(self):
        # print("DEC")
        self.decode()

        if gv.debug_timing:
            print(str(self.env.now) + ": Issued", str(self.instr))

        yield self.env.process(gv.pipeline.get_prev("DECODE").do())

    def decode(self):
        self.instr = gv.pipeline.pipe[Stages["DECODE"]]

        if self.instr:
            self.instr.decode()

            # check for jump
            if self.instr.isUncondBranch:
                gv.fu.jump(self.instr.target)
                self.instr = instruction.getNOP()

            gv.pipeline.pipe[Stages["DECODE"]] = self.instr
            gv.ROB.append(self.instr)
