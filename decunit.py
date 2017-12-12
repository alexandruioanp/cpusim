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
        self.last_branch = None

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

        # if gv.debug_timing:
        #     print("ID@", str(self.env.now) + ":", [x.asm for x in self.instr_bundle])

        self.status = "BUSY"

        self.instr_bundle = self.last_bundle
        gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle

        # TODO: check if there is space in ROB; stall otherwise
        while self.last_bundle:
            if gv.debug_timing:
                print("ID@", str(self.env.now) + ":", [x.asm for x in self.instr_bundle])
            instr = self.last_bundle[0] # peek
            rs_full = gv.stages[Stages["RS"]].push(instr)
            # if gv.debug_timing:
                # print("ID pushed", instr, "to RS");
            if rs_full:
                yield self.env.timeout(1)
            else:
                ii = self.last_bundle.popleft()
                # if gv.debug_timing:
                #     print("ID popped", ii)
                gv.ROB.append(instr)

                gv.R.lock_regs(instr.get_all_regs_touched(), instr)

                if gv.speculationEnabled:
                    instr.isSpeculative = gv.speculating

                if instr and instr.isBranch:
                    if gv.speculationEnabled:
                        if gv.block_on_nested_speculation and gv.speculating:
                            if gv.debug_spec:
                                print("BLOCKING ON SECOND BRANCH", instr)
                            while not (self.last_branch.isExecuted or self.last_branch.isRetired):
                                if gv.debug_spec:
                                    print("waiting on", self.last_branch, self.last_branch.isExecuted, self.last_branch.isRetired)
                                    print([x.asm for x in self.last_bundle])
                                yield self.env.timeout(1)
                            if gv.debug_spec:
                                print("DONE WAITING on", self.last_branch)
                                print(self.last_bundle)
                            # if self.last_branch.isTaken:  # flush bundle
                            #     print("ID flushing bundle before", self.last_bundle)
                            #     self.last_bundle = deque()
                            #     print("ID flushing bundle after", self.last_bundle)
                            #     break
                        # else:
                        if not instr.misspeculated:
                            predTaken = self.brpred.taken(instr)
                            instr.predictedTaken = predTaken
                            gv.speculating = True
                            instr.executedSpeculatively = True
                            self.last_branch = instr
                            if gv.debug_spec:
                                print("AM SPECUL:ATING NOW", instr)
                            if predTaken:
                                if gv.debug_spec:
                                    print("ID: WILL JUMP")
                                gv.fu.jump(instr, speculative=True)
                                if gv.debug_spec:
                                    print("last bundle", [x.asm for x in self.last_bundle])
                                self.last_bundle = deque() # ?
                                break
                    else:
                        while not instr.isExecuted:
                            yield self.env.timeout(1)
                        if instr.isTaken:  # flush bundle
                            self.last_bundle = deque()
                            break

        self.status = "READY"

    def flush(self):
        if gv.debug_spec:
            print("ID bundle flushed", [x.asm for x in self.last_bundle])
        self.last_bundle = deque()
        gv.pipeline.pipe[Stages["DECODE"]] = []

