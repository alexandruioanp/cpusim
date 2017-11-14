import gv
from pipeline import *

class ExecUnit:
    def __init__(self, env):
        self.env = env
        self.bypassed = None

    def do(self):
        # print("EXECUTING")
        self.instr = gv.pipeline.pipe[Stages["EXECUTE"]]

        if self.instr:

            print("EXECUTING", self.instr)

            if self.instr.opcode == "HALT":
                pass
                print("YAAAAAAAASS")

            print("E ", self.env.now)
            gv.unit_statuses[Stages["EXECUTE"]] = "BUSY"

            self.instr.evaluate_operands(self.bypassed)

            self.instr.execute()

            if gv.debug_timing:
                print(str(self.env.now) + ": Executed", str(self.instr))

            self.bypassed = None

            try:
                self.bypassed = (self.instr.dest, self.instr.result)
            except AttributeError:
                pass

            yield self.env.timeout(self.instr.duration)

            print("EXECUTED", self.instr)

            self.instr.is_complete = True
            gv.instr_exec += 1

            gv.unit_statuses[Stages["EXECUTE"]] = "READY"
