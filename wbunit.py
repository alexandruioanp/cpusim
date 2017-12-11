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
        if gv.ROB and gv.debug_timing:
            print("(ex, sp)", [(x.asm, x.isExecuted, x.isSpeculative) for x in gv.ROB])
        try:
            for i in range(gv.retire_rate):
                if gv.ROB[0].isExecuted:
                    instr = gv.ROB.popleft()
                    instr.writeback()

                    # print("Writing back", instr)
                    if gv.debug_timing:
                        print(instr.asm + ", ", end='')
                    instr.isRetired = True

                    if instr.isCondBranch:
                        if gv.speculationEnabled:
                            if gv.debug_spec:
                                print("Resolving speculation because of", instr)
                                print("Pending branches:", [(x.asm, x.isExecuted) for x in gv.branches])

                            self.resolveSpeculation(instr)

                            while gv.ROB[0].misspeculated:
                                instr3 = gv.ROB.popleft()
                                instr3.isRetired = True
                                if gv.debug_spec:
                                    print("flushing, (ex, spec)")
                                    print([(x.asm, x.isExecuted, x.isSpeculative) for x in gv.ROB])

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
        found = False

        if gv.branches[0] != instr:
            if gv.debug_spec:
                print("other pending branches", [(x.asm, x.isExecuted) for x in gv.branches])
            return

        if instr.correctPrediction: # prediction correct
            if gv.debug_spec:
                print("CORRECT")
            for instr2 in gv.ROB:
                if instr2.isCondBranch:
                    if gv.debug_spec:
                        print("HIT BRANCH", instr2)
                    break
                if instr2.isSpeculative:# and not instr.misspeculated:
                    instr2.isSpeculative = False
                    if gv.debug_spec:
                        print(instr2, "not speculative anymore")

        else: # prediction wrong
            for instr2 in gv.ROB:
                if instr2.isSpeculative:
                    instr2.misspeculated = True
                    # instr2.isExecuted = True
                    if gv.debug_spec:
                        print(instr2, "misspeculated")

        if gv.debug_spec:
            print("AFTER RESOLVING SPECULATION (ex, spec)")
            print([(x.asm, x.isExecuted, x.isSpeculative) for x in gv.ROB])

        if gv.debug_spec:
            print("branches before:", [x.asm for x in gv.branches])
        gv.branches.remove(instr)

        if gv.debug_spec:
            print("branches after:", [x.asm for x in gv.branches])

        if not gv.branches:
            gv.speculating = False
            if gv.debug_spec:
                print("DONE SPECULATING @ WB")
