import gv
from pipeline import *
from instruction import *
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

        assert len(gv.ROB) <= gv.ROB_entries

        self.writeback()

        yield self.env.timeout(1)

    def writeback(self):
        if gv.ROB and gv.debug_timing:
            print("(ex, sp)", [(x.asm, x.pc, x.isExecuted, x.isSpeculative) for x in gv.ROB])
        # try:
        for i in range(gv.retire_rate):
            if gv.speculationEnabled:
                if gv.ROB and gv.ROB[0].isExecuted:
                    instr = gv.ROB[0]
                    instr.isRetired = True

                    if not instr.isSpeculative:
                        gv.ROB.popleft()
                        instr.writeback()
                        if gv.reg_renaming:
                            self.release_tags(instr)

                        if not instr.opcode == "JMP": # CHEAT
                            gv.retired += 1
                            if gv.print_trace:
                                print(instr)

                        if instr.opcode == "HALT":
                            self.haltRetired = True
                            return

                    if gv.debug_timing:
                        print(instr.asm + ", ", end='')

                    if instr.isBranch:
                        gv.num_branches += 1

                        if instr.isCondBranch:
                            gv.cond_br += 1

                        if gv.debug_spec:
                            print("Resolving speculation because of (spec, ex)", instr, instr.isSpeculative, instr.isExecuted)

                        self.resolveSpeculation(instr)

                        while gv.ROB and gv.ROB[0].misspeculated:
                            instr3 = gv.ROB.popleft()
                            instr3.isRetired = True
                            if gv.debug_spec:
                                print("flushing, (ex, spec)")
                                print([(x.asm, x.pc, x.isExecuted, x.isSpeculative) for x in gv.ROB])

                            if gv.reg_renaming:
                                gv.R.release_tags(instr3)
                        # nested speculation
                        gv.speculating = False

                        if gv.debug_spec:
                            print("Resolved speculation @ WB. Spec?", gv.speculating)
                else:
                    break
            else:
                if gv.ROB and gv.ROB[0].isExecuted:
                    instr = gv.ROB.popleft()
                    if gv.print_trace:
                        print(instr)
                    if gv.debug_timing:
                        print(instr.asm + ", ", end='')
                    instr.writeback()
                    if gv.reg_renaming:
                        self.release_tags(instr)
                    instr.isRetired = True
                    gv.retired += 1
                    if instr.opcode == "HALT":
                        self.haltRetired = True
                        return
                else:
                    break
        # except IndexError:
            # print("WHOPOP")
            # pass # ROB empty

        if gv.debug_timing:
            print("")

    def release_tags(self, instr):
        if gv.debug_ren:
            print("ROB is", [x.asm for x in gv.ROB])
        tags_in_use = self.get_tags_in_ROB()
        for tag in instr.get_all_regs_touched():
            if gv.debug_ren:
                print(instr, "wants to free", tag)
            if tag in tags_in_use:
                if gv.debug_ren:
                    print("WILL NOT RELEASE TAG", tag)
            else:
                gv.R.release_tag(tag)

    def get_tags_in_ROB(self):
        tags = []
        import itertools
        for instr in list(itertools.islice(gv.ROB, 1)):
            tags += (instr.get_all_regs_touched())
            if gv.debug_ren:
                print("instr using tags", instr, instr.get_all_regs_touched())

        if gv.debug_ren:
            print("TAGS IN USE", tags, "by", [gv.R.reg_from_tag(x) for x in tags])


        return tags

    def is_full(self):
        return len(gv.ROB) == gv.ROB_entries

    def resolveSpeculation(self, instr):
        if instr.isTaken != instr.predictedTaken or (isinstance(instr, JUMPInstruction) and instr.wrongTarget): # wrong
            instr.correctPrediction = False
            if gv.debug_spec:
                print("MUST UNDO")
                print(instr, "was", instr.isTaken, "prediction", instr.predictedTaken)
            gv.fu.undoSpeculation(instr)
            gv.R.undoSpeculation()
            gv.stages[Stages["DECODE"]].flush()
            gv.mispred += 1
        else:
            instr.correctPrediction = True

        hit_branch = False

        if instr.correctPrediction: # prediction correct
            if gv.debug_spec:
                print("CORRECT")
            for instr2 in gv.ROB:
                if instr2.isBranch:
                    hit_branch = True
                    if gv.debug_spec:
                        print("HIT BRANCH", instr2)
                    # break
                if instr2.isSpeculative:
                    instr2.isSpeculative = False
                    if gv.debug_spec:
                        print(instr2, "not speculative anymore")
                if hit_branch:
                    break
        else: # prediction wrong
            for instr2 in gv.ROB:
                if instr2.isSpeculative:
                    instr2.misspeculated = True
                    if gv.debug_spec:
                        print(instr2, "misspeculated")

        if gv.debug_spec:
            print("AFTER RESOLVING SPECULATION (ex, spec)")
            print([(x.asm, x.pc, x.isExecuted, x.isSpeculative) for x in gv.ROB])
