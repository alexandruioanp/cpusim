import gv
from pipeline import *
import instruction

class DecUnit:
    def __init__(self, env):
        self.env = env
        # gv.stages.append(self)

    def do(self):
        # print("DEC")
        self.decode()
        # print("DEC", self.env.now)
        yield self.env.process(gv.pipeline.get_prev("DECODE").do())

    def decode(self):
        instr = gv.pipeline.pipe[Stages["DECODE"]]
        gv.unit_statuses[Stages["DECODE"]] = "BUSY"

        if instr:
            instr.decode()

            # check for jump?
            if instr.isUncondBranch:
                gv.fu.jump(instr.target)
                gv.pipeline.pipe[Stages["DECODE"]] = instruction.getNOP()


        # check for hazard? -- ??
        # if hazard
            # save instruction
            # feed NOP(s?)
            # next time, feed actual instruction
        # self.saved_instr

        gv.unit_statuses[Stages["DECODE"]] = "READY"
