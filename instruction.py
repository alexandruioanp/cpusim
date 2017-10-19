import sys

import gv

def get_instruction(line):
    opcode = line.split(' ')[0]

    try:
        i = instruction_types[opcode](line)
    except KeyError:
        print("Unrecognised instruction", line)
        i = ""

    return i

def getNOP():
    return NOPInstruction("")

debug = True
debug = False

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
        self.operand_vals = []
        self.src = []
        self.dest = []

    def decode(self):
        pass

    def evaluate_operands(self, bypass):
        if debug:
            print("-" * 30)
        try:
            (reg, val) = bypass
        except TypeError:
            reg = val = -1

        if debug:
            print(str(self))

        for idx, src in enumerate(self.src):
            if debug:
                print(idx, ".src", src)
            try:
                src = int(src)

                if debug:
                    print("using immediate value")
                self.operand_vals.append(src)
            except ValueError:
                if src == reg:
                    if debug:
                        print("WILL REPLACE REG", str(reg), "with", val)
                    self.operand_vals.append(val)
                else:
                    if debug:
                        print("Will get from reg")
                    self.operand_vals.append(gv.R.get(int(src[1:])))

    def execute(self):
        pass

    def writeback(self):
        pass


class WRITEBACKInstruction(Instruction):
    def writeback(self):
        gv.R.set(int(self.dest[1:]), self.result)


class XORInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0] ^ self.operand_vals[1]


class WRSInstruction(Instruction):
    def decode(self):
        self.src = [int(self.operands[0])]

    def execute(self):
        while gv.data_mem[self.operand_vals[0]]:
            sys.stdout.write(chr(gv.data_mem[self.operand_vals[0]])),
            self.operand_vals[0] += 1

# STORE R5,R3,0 (src -> dest + offset)
class STOREInstruction(Instruction):
    def decode(self):
        self.src = list(self.operands)

    def execute(self):
        gv.data_mem[self.operand_vals[1] + self.operand_vals[2]] = self.operand_vals[0]


# LOAD R5,R0,8 (src <- dest + offset)
class LOADInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = gv.data_mem[self.operand_vals[0] + self.operand_vals[1]]


# LDI R2,76 (dest = imm)
class LDIInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0]


# WR R5
class WRInstruction(Instruction):
    def decode(self):
        self.src = list(self.operands)

    def execute(self):
        sys.stdout.write(str(self.operand_vals[0]))


# SUBI R6,R1,0 (dest = src - imm) /// SUB R5,R2,R0 (dest = src1 - src2)
class SUBInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0] - self.operand_vals[1]


# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class ADDInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0] + self.operand_vals[1]


class HALTInstruction(Instruction):
    pass

class NOPInstruction(Instruction):
    pass

instruction_types = {
        "XOR": XORInstruction,
        "WRS": WRSInstruction,
        "WR": WRInstruction,
        "HALT": HALTInstruction,
        "STORE": STOREInstruction,
        # "RD": RDInstruction,
        # "BGEZ": BGEZInstruction,
        # "BLTZ": BLTZInstruction,
        # "BEQZ": BEQZInstruction,
        # "BNEZ": BNEZInstruction,
        # "JMP": JMPInstruction,
        # "JUMP": JUMPInstruction,
        "LOAD": LOADInstruction,
        "ADDI": ADDInstruction,
        "SUBI": SUBInstruction,
        # "MULI": MULIInstruction,
        # "DIVI": DIVIInstruction,
        "ADD": ADDInstruction,
        "SUB": SUBInstruction,
        # "MUL": MULInstruction,
        # "DIV": DIVInstruction,
        "LDI": LDIInstruction,
        "NOP": NOPInstruction
    }
