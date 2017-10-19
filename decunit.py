import gv
from pipeline import *
import instruction

class DecUnit:
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
