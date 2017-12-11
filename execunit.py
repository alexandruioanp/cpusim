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

        if instr.misspeculated:
            print("TRYING TO EXECUTE MISSPECULATED ISNTR")

        if instr and not instr.misspeculated:
            self.instr = instr

            if gv.debug_timing:
                print("ES@", self.env.now, instr.asm)

            instr.execute()

            yield self.env.timeout(instr.duration - 0.1)

            if gv.debug_timing:
                print("EF@", self.env.now, instr.asm)

            self.bypassed = None

            try:
                if instr.dest:
                    self.bypassed = (instr.dest, instr.result)
                    # print(instr, instr.dest, instr.result)
            except AttributeError:
                pass

            instr.isExecuted = True

            if not instr.misspeculated:
                gv.instr_exec += 1

        self.status = "READY"
