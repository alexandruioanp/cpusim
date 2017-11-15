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

        # if self.status == "READY":

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
        # self.env.process(gv.pipeline.issue(self.last_bundle))
        while self.last_bundle:
            if gv.stages[Stages["RS"]].status == "READY":  # slot available in RS, issue
                instr = self.last_bundle.popleft()
                gv.ROB.append(instr)
                st = gv.stages[Stages["RS"]].push(instr)
                if st:
                    print("RS cannot accept more")
            else:
                yield self.env.timeout(1)

        self.status = "READY"


        # else:
            # print("DECODE busy")

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

        self.status = "BUSY"

        gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle
        self.instr_bundle = self.last_bundle
        while self.pipe[Stages["DECODE"]]:
            yield self.env.timeout(1)

        self.status = "READY"
