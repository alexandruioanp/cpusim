import gv
from pipeline import *
import simpy

class ExecUnit:
    def __init__(self, env):
        self.env = env
        self.bypassed = None

    def do(self):
        try:
            # while True:
            self.instr = gv.pipeline.pipe[Stages["EXECUTE"]]

            if self.instr:
                # print("EXECUTING", self.instr)

                if gv.debug_timing:
                    print("E ", self.env.now)

                gv.unit_statuses[Stages["EXECUTE"]] = "BUSY"

                self.instr.evaluate_operands(self.bypassed)

                self.instr.execute()

                yield self.env.timeout(self.instr.duration - 0.1)

                if gv.debug_timing:
                    print(str(self.env.now) + ": Executed", str(self.instr))

                self.bypassed = None

                try:
                    self.bypassed = (self.instr.dest, self.instr.result)
                except AttributeError:
                    pass

                self.instr.is_complete = True
                gv.instr_exec += 1

                gv.unit_statuses[Stages["EXECUTE"]] = "READY"
                # yield self.env.timeout(0.1)
                # yield self.env.timeout(1)
            # else:
                # yield self.env.timeout(1)
        except simpy.Interrupt:
            return
