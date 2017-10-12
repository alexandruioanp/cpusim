class FetchUnit:
    def __init__(self, istream):
        self.instruction_ptr = 0
        self.instruction_stream = istream

    def fetch(self, num):
        while self.instruction_ptr < len(self.instruction_stream):
            instr = self.instruction_stream[self.instruction_ptr:self.instruction_ptr + num]
            self.instruction_ptr += num

            yield instr

