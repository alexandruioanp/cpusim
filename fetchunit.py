import gv
import simpy
from pipeline import *
import instruction
import copy

class FetchUnit:
    def __init__(self, istream, env):
        self.env = env
        self.pc = 0
        self.instruction_stream = istream
        self.status = "READY"

    def jump(self, target):
        if target > len(self.instruction_stream):
            raise Exception("Jumped to illegal address " + str(target))

        self.pc = target
        gv.pipeline.pipe[Stages["FETCH"]] = [instruction.getNOP()]


    def do(self):
        self.fetch(gv.issue_rate)
        if gv.debug_timing:
            print(str(self.env.now) + ": Fetch")

        yield self.env.timeout(1)

    def fetch(self, num):
        instr = self.instruction_stream[self.pc:self.pc + num]

        if instr:
            instr2 = []
            for i in instr:
                instr2.append(copy.deepcopy(i))

            for i in instr2:
                # if i.isExecuted and not i.isRetired:
                #     print("SHIT")

                i.isExecuted = False
                i.isRetired = False
                i.isTaken = False

            st = gv.pipeline.push(instr2)

            if not st:
                self.pc += num
            else:
                # print("Couldn't fetch new instruction - pipeline stalled")
                pass

    def get_from_stream(self, num):
        while self.pc < len(self.instruction_stream):
            instr = self.instruction_stream[self.pc:self.pc + num]
            self.pc += num

            yield instr
