import gv
from pipeline import *
import simpy

class ExecUnit:
    def __init__(self, env):
        self.env = env
        self.bypassed = None

    def do(self):
        self.instr = gv.pipeline.pipe[Stages["EXECUTE"]]

        gv.unit_statuses[Stages["EXECUTE"]] = "BUSY"
        if self.instr:
            for instr in self.instr:
                if gv.debug_timing:
                    print("E ", self.env.now)

                instr.evaluate_operands(self.bypassed)

                instr.execute()

                yield self.env.timeout(instr.duration - 0.1)

                if gv.debug_timing:
                    print(str(self.env.now) + ": Executed", str(instr))

                self.bypassed = None

                try:
                    self.bypassed = (instr.dest, instr.result)
                except AttributeError:
                    pass

                instr.is_complete = True
                gv.instr_exec += 1

        gv.unit_statuses[Stages["EXECUTE"]] = "READY"