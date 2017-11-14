import gv
from pipeline import *
import instruction

class FetchUnit:
    def __init__(self, istream, env):
        self.env = env
        self.pc = 0
        self.instruction_stream = istream

    def jump(self, target):
        self.pc = target

    def do(self):
        yield self.env.timeout(1)
        self.fetch(1)
        if gv.debug_timing:
            print(str(self.env.now) + ": Fetch")
        print("F", self.env.now)
        # yield self.env.timeout(0)

    def fetch(self, num):
        instr = self.instruction_stream[self.pc:self.pc + num]

        if instr:
            st = gv.pipeline.push(instr[0])
            if not st:
                self.pc += num
            else:
                print("Couldn't fetch new instruction - pipeline stalled")

    def get_from_stream(self, num):
        while self.pc < len(self.instruction_stream):
            instr = self.instruction_stream[self.pc:self.pc + num]
            self.pc += num

            yield instr
