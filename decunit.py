import gv
import simpy
from pipeline import *
import instruction

class DecUnit:
    def __init__(self, env):
        self.env = env
        self.last_bundle = None

    def do(self):
        self.decode()

        if gv.debug_timing:
            print(str(self.env.now) + ": Issued (Decode)", str(self.instr_bundle))

        yield self.env.timeout(1)

    def decode(self):
        self.instr_bundle = gv.pipeline.pipe[Stages["DECODE"]]

        if not self.instr_bundle:
            return

        if self.instr_bundle != self.last_bundle:
            self.last_bundle = []
            for idx, instr in enumerate(self.instr_bundle):
                instr.decode()

                if instr.isUncondBranch:
                    gv.fu.jump(instr.target)
                    self.last_bundle += ([instruction.getNOP()] * (len(self.instr_bundle) - idx))
                    break
                else:
                    self.last_bundle.append(instr)

            # print(self.last_bundle)
            gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle
            gv.ROB.extend(self.last_bundle)
            self.instr_bundle = self.last_bundle

        # self.instr = gv.pipeline.pipe[Stages["DECODE"]]
        #
        # if self.instr and self.instr != self.last_instr:
        #     self.last_instr = self.instr
        #     self.instr.decode()
        #
        #     # check for jump
        #     if self.instr.isUncondBranch:
        #         gv.fu.jump(self.instr.target)
        #         self.instr = instruction.getNOP()
        #
        #     gv.pipeline.pipe[Stages["DECODE"]] = self.instr
        #     gv.ROB.append(self.instr)
