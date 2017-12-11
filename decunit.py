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

    def do(self):
        self.instr_bundle = gv.pipeline.pipe[Stages["DECODE"]]

        if not self.instr_bundle:
            return

        if self.instr_bundle != self.last_bundle:
            self.last_bundle = deque()
            for idx, instr in enumerate(self.instr_bundle):
                instr.decode()

                if instr.isUncondBranch:
                    gv.fu.jump(instr.target) # if not speculative??
                    if gv.debug_timing:
                        print("@ID jumped", instr)
                    # self.last_bundle += ([self.getDecodedNOP()] * (len(self.instr_bundle) - idx))
                    # self.last_bundle = []
                    break
                else:
                    self.last_bundle.append(instr)

        if gv.debug_timing:
            print("ID@", str(self.env.now) + ":", [x.asm for x in self.instr_bundle])

        self.status = "BUSY"

        self.instr_bundle = self.last_bundle
        gv.pipeline.pipe[Stages["DECODE"]] = self.last_bundle

        # TODO: check if there is space in ROB; stall otherwise
        while self.last_bundle:
            instr = self.last_bundle[0] # peek
            st = gv.stages[Stages["RS"]].push(instr)
            if st:
                # print("RS full, cannot push")
                yield self.env.timeout(1)
            else:
                self.last_bundle.popleft()
                gv.ROB.append(instr)

                # while instr.opcode == "HALT" and not instr.isSpeculative:
                #     # print("COULD STOP")
                #     yield self.env.timeout(1)

                # print([str(x) for x in gv.ROB])
                gv.R.lock_regs(instr.get_all_regs_touched(), instr)

                if gv.speculationEnabled:
                    instr.isSpeculative = gv.speculating

                if instr and instr.isCondBranch:
                    if gv.speculationEnabled:
                        gv.branches.append(instr)
                        if gv.block_on_nested_speculation and gv.speculating:
                            if gv.debug_spec:
                                print("BLOCKING ON SECOND BRANCH", instr)
                            while not (instr.isExecuted or instr.isRetired):
                                yield self.env.timeout(1)
                                if gv.debug_spec:
                                    print("WAITING on", instr, instr.isRetired, )
                            if instr.isTaken:  # flush bundle
                                self.last_bundle = [self.getDecodedNOP()]
                                # gv.pipeline.pipe[Stages["DECODE"]] = [instruction.getNOP()]
                                break
                        else:
                            # print("Will speculate", instr)
                            # if gv.speculating:
                            #     print("blocking")
                            #     self.wait_for_instr(instr)

                            predTaken = self.brpred.taken(instr)
                            # print(instr, "will be predicted as", predTaken)
                            instr.predictedTaken = predTaken
                            instr.executedSpeculatively = True
                            gv.speculating = True
                            if gv.debug_spec:
                                print("AM SPECUL:ATING NOW", instr)
                            # instr.isSpeculative = True
                            if predTaken:
                                gv.fu.jump(instr.target, speculative=True)
                    else:
                        while not instr.isExecuted:
                            yield self.env.timeout(1)
                        if instr.isTaken:  # flush bundle
                            self.last_bundle = [self.getDecodedNOP()]
                            # gv.pipeline.pipe[Stages["DECODE"]] = [instruction.getNOP()]
                            break

        self.status = "READY"

    def wait_for_instr(self, instr):
        while not instr.isExecuted:
            print("still waiting")
            yield self.env.timeout(1)
            if instr.isTaken:  # flush bundle
                self.last_bundle = []
                gv.pipeline.pipe[Stages["DECODE"]] = []
                break

    def getDecodedNOP(self):
        nop = instruction.getNOP()
        nop.decode()
        return nop
