import gv
from pipeline import *

class WBUnit:
    def __init__(self):
        pass

    def writeback(self):
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]
        gv.unit_statuses[Stages["WRITEBACK"]] = "BUSY"

        if instr:
            instr.writeback()
            gv.pipeline.pipe[Stages['WRITEBACK']] = None

        gv.unit_statuses[Stages["WRITEBACK"]] = "READY"

        return instr

