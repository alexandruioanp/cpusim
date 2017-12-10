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
            self.savedPCs.append(self.pc)
            # print("will continue from", self.pc, "which is", self.instruction_stream[self.pc])
            # print(self.savedPCs)

        self.pc = target
        gv.pipeline.pipe[Stages["FETCH"]] = [getNOP()]

    def undoSpeculation(self, instr):
        print("UNDOINGGGGGGGGGGGGG", self.savedPCs)
        self.pc = self.savedPCs[0]
        self.savedPCs = self.savedPCs[1:]
        print("AFTERRR", self.savedPCs)
        print("gv.speculating", gv.speculating)
        if not self.savedPCs:
            print("DONE SPECULATING, jumping to", self.pc)

            gv.speculating = False

    def do(self):
        self.fetch(gv.issue_rate)
        yield self.env.timeout(1)

    def fetch(self, num):
        instr = self.instruction_stream[self.pc:self.pc + num]

        if gv.debug_timing:
            print("Fe@", str(self.env.now) + ": ", end='')

        if instr:
            instr2 = []
            for i in instr:
                instr_obj = get_instruction(i)
                instr_obj.isSpeculative = gv.speculating
                instr2.append(instr_obj)
                print(i, "speculating", gv.speculating, "isspec", instr2[-1].isSpeculative)

            if gv.debug_timing:
                print(instr2, ' ', end='')

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
