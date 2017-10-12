import global_vars
from pipeline import *

class ExecUnit:
    def __init__(self):
        pass

    def execute(self):
        instr = global_vars.pipeline.pipe[Stages["EXECUTE"]]
        if instr:
            instr.execute()