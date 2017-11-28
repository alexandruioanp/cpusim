import gv
from pipeline import *
import simpy

class ExecUnit:
    def __init__(self, env, id, result_bus):
        self.env = env
        self.bypassed = None
        self.result_bus = result_bus
        self.id = id
        self.status = "READY"
        self.instr = None

    def do(self, instr):
        self.status = "BUSY"
        self.bypassed = None

        if instr:
            self.instr = instr

            if gv.debug_timing:
                print("E" + str(self.id), self.env.now)
            instr.execute()

            yield self.env.timeout(instr.duration - 0.1)

            if gv.debug_timing:
                print(str(self.env.now) + ": Executed", str(instr))

            self.bypassed = None

            try:
                if instr.dest:
                    self.bypassed = (instr.dest, instr.result)
                    # print(instr, instr.dest, instr.result)
            except AttributeError:
                pass

            instr.isExecuted = True
            gv.instr_exec += 1

        self.status = "READY"
