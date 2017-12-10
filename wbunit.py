import gv
from pipeline import *
import instruction
from collections import deque
import simpy

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = []
        gv.ROB = deque()
        gv.retired = 0
        self.haltRetired = False

    def do(self):
        if gv.debug_timing:
            print("WB@ " + str(self.env.now) + ": ", end='')

        self.writeback()

        yield self.env.timeout(1)

    def writeback(self):
        # self.last_instr = []
        if gv.ROB and gv.debug_timing:
            print([(str(x), x.isExecuted, x.isSpeculative) for x in gv.ROB])
        try:

            for i in range(gv.retire_rate):
                if gv.ROB[0].isSpeculative:
                    if gv.debug_spec:
                        print("ROB[0] is speculative", [str(x) for x in gv.ROB])
                    if gv.ROB[0].misspeculated:
                        instr = gv.ROB.popleft()
                        instr.isRetired = True
                        if gv.debug_spec:
                            print("flushing")
                            print([(str(x), x.isExecuted, x.isSpeculative) for x in gv.ROB])
                        continue
                    # else:
                    #     return

                if gv.ROB[0].isExecuted:
                    instr = gv.ROB.popleft()
                    instr.writeback()
                    if instr.isCondBranch:
                        # print("retiring conditional branch")
                        if gv.speculationEnabled:
                            if gv.debug_spec:
                                print("Resolving speculation because of", instr)
                            self.resolveSpeculation(instr)
                    print("Writing back", instr)
                    if gv.debug_timing:
                        print(str(instr) + ", ", end='')
                    instr.isRetired = True
                    # self.last_instr.append(instr)
                    gv.retired += 1
                    if instr.opcode == "HALT":
                        # print("RETIRED HALT")
                        self.haltRetired = True
                        return
                else:
                    break
        except IndexError:
            pass # ROB empty

        if gv.debug_timing:
            print("")

    def resolveSpeculation(self, instr):
        hitBranch = False

        for instr2 in gv.ROB:
            if instr2.isCondBranch:
                hitBranch = True
                # break
            if instr.correctPrediction:
                if not instr.misspeculated:
                    instr2.isSpeculative = False
                    if gv.debug_spec:
                        print(instr2, "not speculative anymore")
            else:
                instr2.misspeculated = True
                if gv.debug_spec:
                    print(instr2, "misspeculated")
        print("AFTER RESOLVING SPECULATION (ex, spec)")
        print([(str(x), x.isExecuted, x.isSpeculative) for x in gv.ROB])
