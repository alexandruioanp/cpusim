import gv
from pipeline import *

class DecUnit:
    def decode(self):
        instr = gv.pipeline.pipe[Stages["DECODE"]]
        gv.unit_statuses[Stages["DECODE"]] = "BUSY"
        if instr:
            instr.decode()
        gv.unit_statuses[Stages["DECODE"]] = "READY"
