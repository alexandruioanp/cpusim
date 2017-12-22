import simpy
from collections import deque

import gv
from pipeline import *
import instruction
from brpredictor import *

class DecUnit:
    def __init__(self, env):
        self.env = env
        self.last_bundle = None
        self.status = "READY"
        self.brpred = BrPredictor()
        gv.br_pred = self.brpred
        self.last_branch = None
        self.instr_bundle = []

    def do(self):
        self.instr_bundle = gv.pipeline.pipe[Stages["DECODE"]]

        if not self.instr_bundle:
            return

        if self.instr_bundle != self.last_bundle:
            self.last_bundle = deque()
            for idx, instr in enumerate(self.instr_bundle):
                instr.decode()

                if not gv.speculationEnabled:
                    if instr.isUncondBranch:
                        gv.fu.jump(instr)
                        break
                    else:
                        self.last_bundle.append(instr)
                else:
                    self.last_bundle.append(instr)
                    if instr.isUncondBranch:
                        break

                if gv.reg_renaming:
                    gv.R.rename(instr)

        self.status = "BUSY"

        self.instr_bundle = self.last_bundle
        gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle

        if gv.debug_timing:
            print("ID@", str(self.env.now) + ":", [x.asm for x in self.instr_bundle])

        while self.last_bundle:
            instr = self.last_bundle[0] # peek

            if gv.stages[Stages["RS"]].is_full():
                if gv.wb.haltRetired:
                    return
                if gv.debug_timing:
                    print(">>>>>>>>>>>>>> RS FULL")
                yield self.env.timeout(1)

            elif gv.wb.is_full():
                if gv.debug_timing:
                    print(">>>>>>>>>>>>>> ROB FULL")
                yield self.env.timeout(1)

            else:
                if gv.speculationEnabled:
                    if instr.isBranch:
                        # nested
                        if gv.block_on_nested_speculation and gv.speculating:
                            if gv.debug_spec:
                                print("BLOCKING ON SECOND BRANCH", instr)
                            while not self.last_branch.isRetired:
                                if gv.wb.haltRetired:
                                    return

                                if gv.debug_spec:
                                    print("waiting on", self.last_branch, self.last_branch.isExecuted,
                                          self.last_branch.isRetired)
                                    print([x.asm for x in self.last_bundle])

                                yield self.env.timeout(1)

                            if gv.debug_spec:
                                print("DONE WAITING on", self.last_branch)
                                print("last bundle", [x.asm for x in self.last_bundle])

                        if not instr.misspeculated:
                            self.issue(instr)
                            if gv.debug_spec:
                                print("ID will issue (misspec?)", instr, instr.misspeculated)
                            instr.predictedTaken = self.brpred.taken(instr)
                            gv.speculating = True
                            self.last_branch = instr
                            if gv.debug_spec:
                                print("AM SPECULATING NOW", instr)
                            gv.R.speculate()
                            if instr.predictedTaken:
                                instr.executedSpeculatively = True
                                if gv.debug_spec:
                                    print("ID: WILL JUMP")
                                gv.fu.jump(instr, speculative=True)
                                if gv.debug_spec:
                                    print("last bundle", [x.asm for x in self.last_bundle])
                                self.last_bundle = deque()  # ?
                                break
                    else:
                        self.issue(instr)
                else:
                    self.issue(instr)

                    if instr.isBranch:
                        while not instr.isExecuted:
                            if gv.wb.haltRetired:
                                return
                            if gv.debug_spec:
                                print("waiting on", instr)
                            yield self.env.timeout(1)
                        if instr.isTaken:
                            self.last_bundle = deque()
                            break

        self.status = "READY"

    def issue(self, instr):
        assert self.last_bundle.popleft() == instr

        if gv.debug_timing:
            print("ID pushed", instr, "to RS");

        gv.ROB.append(instr)
        gv.stages[Stages["RS"]].push(instr)

        gv.R.lock_regs(instr.get_all_regs_touched(), instr)

        if gv.speculationEnabled:
            instr.isSpeculative = gv.speculating

    def flush(self):
        if gv.debug_spec:
            print("Flushing ID bundle", [x.asm for x in self.last_bundle])
        for instr in self.last_bundle:
            instr.misspeculated = True
        self.last_bundle = deque()
        gv.pipeline.pipe[Stages["DECODE"]] = []

