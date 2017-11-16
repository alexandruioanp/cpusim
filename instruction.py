import sys
import operator

import simpy

import gv
from pipeline import *

def get_instruction(line):
    opcode = line.split(' ')[0]

    try:
        i = instruction_types[opcode](line)
    except KeyError:
        print("Unrecognised instruction", line)
        i = ""

    return i

def getNOP():
    return NOPInstruction("NOP")

debug = True
debug = False

class Instruction():
    def __str__(self):
        return self.opcode + " " + str(self.operands)

    def __init__(self, asm):
        comps = asm.split(' ')
        self.opcode = comps[0]

        self.isBranch = True if self.opcode in ["BGEZ", "BLTZ", "BEQZ", "BNEZ", "JMP", "JUMP"] else False
        self.isUncondBranch = True if self.opcode in ["JMP"] else False # , "JUMP"
        self.isCondBranch = not self.isUncondBranch

        if len(comps) > 1:
            self.operands = comps[1]
            self.operands = self.operands.split(',')
        else:
            self.operands = ""
        self.operand_vals = []
        self.src = []
        self.dest = []
        self.duration = 1

        self.isComplete = False
        self.canDispatch = True

    def get_reg_nums(self):
        regs_src = []
        regs_dest = []

        for op in self.src:
            try:
                if op[0] == "R":
                    reg_num = int(op[1:])
                    regs_src.append(reg_num)
            except TypeError:
                pass  # is literal

        op = self.dest
        if op:
            try:
                if op[0] == "R":
                    reg_num = int(op[1:])
                    regs_dest.append(reg_num)
            except TypeError:
                pass  # is literal

        return {"src": regs_src, "dest": regs_dest}

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
            print("Evaluating", str(self))

        self.operand_vals = []

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


class BRANCHInstruction(Instruction):
    pass


class MEMInstruction(Instruction):
    def __init__(self, *args, **kwargs):
        super(MEMInstruction, self).__init__(*args, **kwargs)
        self.duration = 5


class JMPInstruction(BRANCHInstruction):
    def decode(self):
        self.target = int(self.operands[0])

    def execute(self):
        print("PROBLEM? EXECUTED JMP")


class JUMPInstruction(BRANCHInstruction):
    def decode(self):
        self.src = [self.operands[0]]

    def execute(self):
        gv.fu.jump(self.operand_vals[0])


class CONDBRANCHInstruction(BRANCHInstruction):
    def decode(self):
        self.src = [self.operands[0]]
        self.target = int(self.operands[1])

        if self.opcode == "BGEZ":
            self.operator = operator.ge
        elif self.opcode == "BLTZ":
            self.operator = operator.lt
        elif self.opcode == "BEQZ":
            self.operator = operator.eq
        elif self.opcode == "BNEZ":
            self.operator = operator.ne

    def execute(self):
        if self.operator(self.operand_vals[0], 0):
            gv.fu.jump(self.target)

            gv.pipeline.pipe[Stages["DECODE"]] = getNOP() # here
        else:
            pass


class WRITEBACKInstruction(Instruction):
    def writeback(self):
        if debug:
            print("WRITING", str(self))
            print(self.dest)
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
class STOREInstruction(MEMInstruction):
    def decode(self):
        self.src = list(self.operands)

    def execute(self):
        a = self.operand_vals[0] & 0xFF
        b = (self.operand_vals[0] >> 8)  & 0xFF
        c = (self.operand_vals[0] >> 16) & 0xFF
        d = (self.operand_vals[0] >> 24) & 0xFF

        gv.data_mem[self.operand_vals[1] + self.operand_vals[2] + 0] = a
        gv.data_mem[self.operand_vals[1] + self.operand_vals[2] + 1] = b
        gv.data_mem[self.operand_vals[1] + self.operand_vals[2] + 2] = c
        gv.data_mem[self.operand_vals[1] + self.operand_vals[2] + 3] = d


# LOAD R5,R0,8 (src <- dest + offset)
class LOADInstruction(WRITEBACKInstruction, MEMInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = 0
        a = gv.data_mem[self.operand_vals[0] + self.operand_vals[1] + 0]
        b = gv.data_mem[self.operand_vals[0] + self.operand_vals[1] + 1]
        c = gv.data_mem[self.operand_vals[0] + self.operand_vals[1] + 2]
        d = gv.data_mem[self.operand_vals[0] + self.operand_vals[1] + 3]
        self.result = a + (b << 8) + (c << 16) + (d << 24)

        if self.result >> 31 == 1:
            self.result = -((0xFFFFFFFF^self.result) + 1)

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


# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class MULInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0] * self.operand_vals[1]



# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class DIVInstruction(WRITEBACKInstruction):
    def decode(self):
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.duration = 3

    def execute(self):
        self.result = int(self.operand_vals[0] / self.operand_vals[1])



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
        "BGEZ": CONDBRANCHInstruction,
        "BLTZ": CONDBRANCHInstruction,
        "BEQZ": CONDBRANCHInstruction,
        "BNEZ": CONDBRANCHInstruction,
        "JMP": JMPInstruction,
        "JUMP": JUMPInstruction,
        "LOAD": LOADInstruction,
        "ADDI": ADDInstruction,
        "SUBI": SUBInstruction,
        "MULI": MULInstruction,
        "DIVI": DIVInstruction,
        "ADD": ADDInstruction,
        "SUB": SUBInstruction,
        "MUL": MULInstruction,
        "DIV": DIVInstruction,
        "LDI": LDIInstruction,
        "NOP": NOPInstruction
    }
