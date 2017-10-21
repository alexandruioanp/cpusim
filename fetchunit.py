import gv
from pipeline import *
import instruction

class FetchUnit:
    def __init__(self, istream):
        self.pc = 0
        self.instruction_stream = istream

    def jump(self, target):
        self.pc = target

    def fetch(self, num):
        gv.unit_statuses[Stages["FETCH"]] = "BUSY"

        instr = self.instruction_stream[self.pc:self.pc + num]
        self.pc += num

        if instr:
            gv.pipeline.push(instr[0])

        gv.unit_statuses[Stages["FETCH"]] = "READY"

        return instr

    def get_from_stream(self, num):
        while self.pc < len(self.instruction_stream):

            instr = self.instruction_stream[self.pc:self.pc + num]
            self.pc += num

            yield instr
