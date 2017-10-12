import global_vars
from pipeline import *

class WBUnit:
    def __init__(self):
        pass

    def writeback(self):
        instr = global_vars.pipeline.pipe[Stages["WRITEBACK"]]
        if instr:
            instr.writeback()
            global_vars.pipeline.pipe[Stages['WRITEBACK']] = None