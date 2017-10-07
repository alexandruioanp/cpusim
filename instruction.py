import sys

def get_instruction(line):
    opcode = line.split(' ')[0]

    try:
        i = instruction_types[opcode](line)
    except KeyError:
        i = ""

    return i

class Instruction:
    def __str__(self):
        return self.opcode + " " + str(self.operands)

    def __init__(self, asm):
        comps = asm.split(' ')
        self.opcode, self.operands = comps
        self.operands = self.operands.split(',')

    def decode(self):
        pass

    def execute(self):
        pass

    def writeback(self):
        pass


class ALUInstruction(Instruction):
    def writeback(self):
        R[self.dest] = self.result


class XORInstruction(ALUInstruction):
    def decode(self):
        self.dest = int(self.operands[0][1:])
        self.src1 = int(self.operands[1][1:])
        self.src2 = int(self.operands[2][1:])

    def execute(self):
        self.result = R[self.src1] ^ R[self.src2]


class WRSInstruction(Instruction):
    def decode(self):
        self.addr = int(self.operands[0])

    def execute(self):
        while data[self.addr]:
            sys.stdout.write(chr(data[self.addr])),
            self.addr += 1


class WRInstruction(Instruction):
    def decode(self):
        self.src = int(self.operands[0][1:])

    def execute(self):
        sys.stdout.write(str(R[self.src]))

class ADDIInstruction(ALUInstruction):
    def decode(self):
        self.dest = int(self.operands[0][1:])
        self.src = int(self.operands[1][1:])
        self.imm = int(self.operands[2])

    def execute(self):
        self.result = R[self.src] + self.imm


instruction_types = {
        "XOR": XORInstruction,
        "WRS": WRSInstruction,
        "WR": WRInstruction,
        # "STORE": STOREInstruction,
        # "RD": RDInstruction,
        # "BGEZ": BGEZInstruction,
        # "BLTZ": BLTZInstruction,
        # "BEQZ": BEQZInstruction,
        # "BNEZ": BNEZInstruction,
        # "JMP": JMPInstruction,
        # "JUMP": JUMPInstruction,
        # "LOAD": LOADInstruction,
        # "IADDR": IADDRInstruction,
        "ADDI": ADDIInstruction,
        # "SUBI": SUBIInstruction,
        # "MULI": MULIInstruction,
        # "DIVI": DIVIInstruction,
        # "ADD": ADDInstruction,
        # "SUB": SUBInstruction,
        # "MUL": MULInstruction,
        # "DIV": DIVInstruction,
        # "LDI": LDIInstruction
        "HALT": None
    }
