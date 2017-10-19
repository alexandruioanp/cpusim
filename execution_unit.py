import gv
from pipeline import *

class ExecUnit:
    def __init__(self):
        self.bypassed = None
        pass

    def execute(self):
        instr = gv.pipeline.pipe[Stages["EXECUTE"]]
        gv.unit_statuses[Stages["EXECUTE"]] = "BUSY"

        if instr:
            instr.evaluate_operands(self.bypassed)
            instr.execute()
            self.bypassed = None

            if gv.enable_forwarding:
                try:
                    self.bypassed = (instr.dest, instr.result)
                except AttributeError:
                    pass

        gv.unit_statuses[Stages["EXECUTE"]] = "READY"
