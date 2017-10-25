import gv
from pipeline import *

class WBUnit:
    def __init__(self, env):
        self.env = env
        pass

    def do(self):
        # print("WB WILL WAIT")
        # wait for prev stage
        self.writeback()
        yield self.env.process(gv.pipeline.get_prev("WRITEBACK").do())

    def writeback(self):
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]
        gv.unit_statuses[Stages["WRITEBACK"]] = "BUSY"

        if instr:
            instr.writeback()
            gv.pipeline.pipe[Stages['WRITEBACK']] = None

        gv.unit_statuses[Stages["WRITEBACK"]] = "READY"

        return instr
