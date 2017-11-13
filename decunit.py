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

    def wait(self):
        # print("DECODE WAITING")
        yield self.env.process(gv.pipeline.get_next("DECODE").wait())

    def decode(self):
        self.instr = gv.pipeline.pipe[Stages["DECODE"]]
        gv.unit_statuses[Stages["DECODE"]] = "BUSY"

        if self.instr:
            self.instr.decode()

            # check for jump
            if self.instr.isUncondBranch:
                gv.fu.jump(self.instr.target)
                gv.pipeline.pipe[Stages["DECODE"]] = instruction.getNOP()
                # gv.ROB.popleft()
                gv.ROB.append(gv.pipeline.pipe[Stages["DECODE"]])
            else:
                gv.ROB.append(self.instr)

        gv.unit_statuses[Stages["DECODE"]] = "READY"
