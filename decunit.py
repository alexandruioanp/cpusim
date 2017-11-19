import gv
import simpy
from pipeline import *
import instruction
from collections import deque

class DecUnit:
    def __init__(self, env):
        self.env = env
        self.last_bundle = None
        self.status = "READY"

    def do(self):
        if gv.debug_timing:
            print(str(self.env.now) + ": Issued (Decode)", str(self.instr_bundle))

        self.instr_bundle = gv.pipeline.pipe[Stages["DECODE"]]

        if not self.instr_bundle:
            return

        if self.instr_bundle != self.last_bundle:
            # self.last_bundle = deque(maxlen=gv.issue_rate)
            self.last_bundle = deque()
            for idx, instr in enumerate(self.instr_bundle):
                instr.decode()

                if instr.isUncondBranch:
                    gv.fu.jump(instr.target)
                    self.last_bundle += ([instruction.getNOP()] * (len(self.instr_bundle) - idx))
                    break
                else:
                    self.last_bundle.append(instr)

        self.status = "BUSY"

        self.instr_bundle = self.last_bundle
        gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle

        while self.last_bundle:
            instr = self.last_bundle[0] # peek
            st = gv.stages[Stages["RS"]].push(instr)
            if st:
                # print("RS full, cannot push")
                yield self.env.timeout(1)
            else:
                self.last_bundle.popleft()
                gv.ROB.append(instr)
                gv.R.lock_regs(instr.get_reg_nums()["dest"], instr)

        self.status = "READY"
