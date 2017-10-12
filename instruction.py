import sys

import global_vars

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
        self.opcode = comps[0]
        if len(comps) > 1:
            self.operands = comps[1]
            self.operands = self.operands.split(',')
        else:
            self.operands = ""

    def decode(self):
        pass

    def execute(self):
        pass

    def writeback(self):
        pass


class ALUInstruction(Instruction):
    def writeback(self):
        global_vars.R.set(self.dest, self.result)


class XORInstruction(ALUInstruction):
    def decode(self):
        self.dest = int(self.operands[0][1:])
        self.src1 = int(self.operands[1][1:])
        self.src2 = int(self.operands[2][1:])

    def execute(self):
        self.result = global_vars.R.get(self.src1) ^ global_vars.R.get(self.src2)


class WRSInstruction(Instruction):
    def decode(self):
        self.addr = int(self.operands[0])

    def execute(self):
        while global_vars.data_mem[self.addr]:
            sys.stdout.write(chr(global_vars.data_mem[self.addr])),
            self.addr += 1


class WRInstruction(Instruction):
    def decode(self):
        self.src = int(self.operands[0][1:])

    def execute(self):
        sys.stdout.write(str(global_vars.R.get(self.src)))


class ADDIInstruction(ALUInstruction):
    def decode(self):
        self.dest = int(self.operands[0][1:])
        self.src = int(self.operands[1][1:])
        self.imm = int(self.operands[2])

    def execute(self):
        self.result = global_vars.R.get(self.src) + self.imm


class HALTInstruction(Instruction):
    pass

instruction_types = {
        "XOR": XORInstruction,
        "WRS": WRSInstruction,
        "WR": WRInstruction,
        "HALT": HALTInstruction,
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
    }
