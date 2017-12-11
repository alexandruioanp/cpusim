import gv
import simpy
from pipeline import *
from instruction import *


class FetchUnit:
    def __init__(self, istream, env):
        self.env = env
        self.pc = 0
        self.instruction_stream = istream
        self.status = "READY"
        self.savedPCs = []

    def jump(self, target, speculative=False):
        if target > len(self.instruction_stream):
            raise Exception("Jumped to illegal address " + str(target))

        if speculative:
            gv.speculation_level += 1
            if gv.debug_spec:
                print("JUMPING SPECULATIVELY to", target, "FROM", self.pc, "gv.spec", gv.speculating)
                print("instruction after return:", self.instruction_stream[self.pc])
            # print("will continue from", self.pc, "which is", self.instruction_stream[self.pc])
            # print(self.savedPCs)

        self.pc = target
        gv.pipeline.pipe[Stages["FETCH"]] = []

    def undoSpeculation(self, instr):
        if gv.debug_spec:
            print("UNDOINGGGGGGGGGGGGG", instr, instr.pc + 1)
        self.pc = instr.pc + 1
        # self.pc = self.savedPCs[0]
        gv.speculation_level -= 1
        if gv.debug_spec:
            print("next to fetch:", self.instruction_stream[self.pc:self.pc+3])
            if gv.pipeline.pipe[Stages["FETCH"]]:
                print("in pipeline", [x.asm for x in gv.pipeline.pipe[Stages["FETCH"]]])

        if not gv.branches:
            if gv.debug_spec:
                print("DONE SPECULATING, jumping to", self.pc)
            gv.speculating = False

        if gv.debug_spec:
            print("gv.speculating", gv.speculating)
        gv.pipeline.pipe[Stages["FETCH"]] = []

    def do(self):
        self.fetch(gv.issue_rate)
        yield self.env.timeout(1)

    def fetch(self, num):
        instr = self.instruction_stream[self.pc:self.pc + num]
        instrpc = self.pc

        if gv.debug_timing:
            print("Fe@", str(self.env.now) + ": ", end='')

        if instr:
            instr2 = []
            for i in instr:
                instr_obj = get_instruction(i)
                instr_obj.isSpeculative = gv.speculating
                instr2.append(instr_obj)
                instr_obj.pc = instrpc
                # if gv.debug_spec:
                    # print(i, "speculating", gv.speculating, "isspec", instr2[-1].isSpeculative)
                if gv.debug_timing:
                    print(i, ' ', end='')
                instrpc += 1

            st = gv.pipeline.push(instr2)

            if not st:
                self.pc += num
            else:
                # print("Couldn't fetch new instruction - pipeline stalled")
                pass

        if gv.debug_timing:
                print("")

    def get_from_stream(self, num):
        while self.pc < len(self.instruction_stream):
            instr = self.instruction_stream[self.pc:self.pc + num]
            self.pc += num

            yield instr
