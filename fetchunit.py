import gv
from pipeline import *
import instruction

class FetchUnit:
    def __init__(self, istream, env):
        self.env = env
        self.pc = 0
        self.instruction_stream = istream
        # gv.stages.append(self).append(self)

    def jump(self, target):
        self.pc = target

    def do(self):
        # yield self.env.process(gv.pipeline.get_prev("FETCH").do())
        self.fetch(1)
        # print("F", self.env.now)
        yield self.env.timeout(0)

    def wait(self):
        # print("FETCH WAITING")
        yield self.env.process(gv.pipeline.get_next("FETCH").wait())

    def fetch(self, num):
        gv.unit_statuses[Stages["FETCH"]] = "BUSY"

        instr = self.instruction_stream[self.pc:self.pc + num]

        if instr:
            st = gv.pipeline.push(instr[0])
            if not st:
                self.pc += num
            else:
                print("Couldn't fetch new instruction - pipeline stalled")

        gv.unit_statuses[Stages["FETCH"]] = "READY"


    def get_from_stream(self, num):
        while self.pc < len(self.instruction_stream):

            instr = self.instruction_stream[self.pc:self.pc + num]
            self.pc += num

            yield instr
