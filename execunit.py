import gv
from pipeline import *

class ExecUnit:
    def __init__(self, env):
        self.env = env
        self.bypassed = None

    def do(self):
        self.execute()
        if self.instr:
            yield self.env.timeout(self.instr.duration - 1)

        yield self.env.process(gv.pipeline.get_prev("EXECUTE").do())


    def wait(self):
        print("EXEC WAITING")
        yield self.env.process(gv.pipeline.get_next("EXECUTE").wait())

    def execute(self):
        # print("EXECUTING")
        self.instr = gv.pipeline.pipe[Stages["EXECUTE"]]
        gv.unit_statuses[Stages["EXECUTE"]] = "BUSY"

        if self.instr:
            gv.instr_exec += 1
            self.instr.evaluate_operands(self.bypassed)
            self.instr.execute()

            self.bypassed = None

            if gv.enable_forwarding:
                try:
                    self.bypassed = (self.instr.dest, self.instr.result)
                except AttributeError:
                    pass

        gv.unit_statuses[Stages["EXECUTE"]] = "READY"
