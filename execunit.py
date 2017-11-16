import gv
from pipeline import *
import simpy

class ExecUnit:
    def __init__(self, env, id):
        self.env = env
        self.bypassed = None
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

        self.status = "READY"
