import gv
import simpy
from pipeline import *
import instruction

class FetchUnit:
    def __init__(self, istream, env):
        self.env = env
        self.pc = 0
        self.instruction_stream = istream
        self.status = "READY"

    def jump(self, target):
        self.pc = target

    def do(self):
        self.fetch(gv.issue_rate)
        if gv.debug_timing:
            print(str(self.env.now) + ": Fetch")

        yield self.env.timeout(1)

    def fetch(self, num):
        instr = self.instruction_stream[self.pc:self.pc + num]

        if instr:
            for i in instr:
                i.isExecuted = False
                i.isRetired = False

            st = gv.pipeline.push(instr)

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
