import gv
from pipeline import *

class ExecUnit:
    def __init__(self, env):
        self.env = env
        self.bypassed = None

    def do(self):
        self.execute()

        yield self.env.process(gv.pipeline.get_prev("EXECUTE").do())

        if gv.debug_timing:
            print(str(self.env.now) + ": Starting execution of " + str(self.instr))

        if self.instr:
            yield self.env.timeout(self.instr.duration - 1)

        if gv.debug_timing:
            print(str(self.env.now) + ": Executed", str(self.instr))

    def execute(self):
        # print("EXECUTING")
        self.instr = gv.pipeline.pipe[Stages["EXECUTE"]]

        if self.instr:
            gv.instr_exec += 1
            self.instr.evaluate_operands(self.bypassed)
            self.instr.execute()

            self.bypassed = None

            try:
                self.bypassed = (self.instr.dest, self.instr.result)
            except AttributeError:
                pass

            self.instr.is_complete = True
