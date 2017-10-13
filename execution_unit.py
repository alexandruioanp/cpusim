import global_vars
from pipeline import *

class ExecUnit:
    def __init__(self):
        self.bypassed = None
        pass

    def execute(self):
        instr = global_vars.pipeline.pipe[Stages["EXECUTE"]]

        if instr:
            instr.evaluate_operands(self.bypassed)
            instr.execute()
            self.bypassed = None

            try:
                self.bypassed = (instr.dest, instr.result)
            except AttributeError:
                pass