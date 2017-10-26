import gv
from pipeline import *
import instruction

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = instruction.getNOP()

    def do(self):
        # print("WB WILL WAIT")
        # wait for prev stage
        # print("WB", self.env.now)
        instr = self.writeback()
        if instr:
            self.last_instr = instr

        yield self.env.process(gv.pipeline.get_prev("WRITEBACK").do())

    def wait(self):
        # print("WB WAITING")
        # yield self.env.process(gv.pipeline.get_next("FETCH").wait())
        yield self.env.timeout(0)

    def writeback(self):
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]
        gv.unit_statuses[Stages["WRITEBACK"]] = "BUSY"

        if instr:
            instr.writeback()
            gv.pipeline.pipe[Stages['WRITEBACK']] = None

        gv.unit_statuses[Stages["WRITEBACK"]] = "READY"

        return instr
