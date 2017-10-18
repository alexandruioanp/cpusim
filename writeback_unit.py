import gv
from pipeline import *

class WBUnit:
    def __init__(self):
        pass

    def writeback(self):
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]
        if instr:
            instr.writeback()
            gv.pipeline.pipe[Stages['WRITEBACK']] = None
