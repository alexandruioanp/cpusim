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
        self.asm = asm

    def __get_reg_nums(self):
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

    def get_src_regs(self):
        return self.srcRegNums

    def get_dest_regs(self):
        return self.destRegNums

    def get_all_regs_touched(self):
        return self.allRegNums

    def set_all_regs_touched(self):
        regsTouched = self.__get_reg_nums()

        self.srcRegNums = list(set(regsTouched["src"]))
        self.destRegNums = list(set(regsTouched["dest"]))
        self.allRegNums = list(set(self.srcRegNums + self.destRegNums))

    def decode(self):
        comps = self.asm.split(' ')
        self.opcode = comps[0]

        self.isBranch = self.opcode in ["BGEZ", "BLTZ", "BEQZ", "BNEZ", "JMP", "JUMP"]
        self.isUncondBranch = self.opcode in ["JMP"]  # , "JUMP"
        self.isCondBranch = self.opcode in ["BGEZ", "BLTZ", "BEQZ", "BNEZ", "JUMP"]
        self.isStore = self.opcode == "STORE"
        self.isLoad = self.opcode == "LOAD"
        self.isMemAccess = self.isStore or self.isLoad

        if len(comps) > 1:
            self.operands = comps[1]
            self.operands = self.operands.split(',')
        else:
            self.operands = ""
        self.operand_vals = []
        self.src = []
        self.dest = []
        self.duration = 1

        self.isExecuted = False
        self.isRetired = False
        self.isTaken = False
        self.canDispatch = True

        self.srcRegNums = []
        self.destRegNums = []
        self.allRegNums = []

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
    def decode(self):
        super(MEMInstruction, self).decode()
        self.duration = 5


class REGWRITEBACKInstruction(Instruction):
    def writeback(self):
        if debug:
            print("WRITING", str(self))
            print(self.dest)
        gv.R.set(int(self.dest[1:]), self.result)


class JMPInstruction(BRANCHInstruction):
    def decode(self):
        super(JMPInstruction, self).decode()
        self.target = int(self.operands[0])
        self.set_all_regs_touched()

    def execute(self):
        print("PROBLEM? EXECUTED JMP")


class JUMPInstruction(BRANCHInstruction):
    def decode(self):
        super(JUMPInstruction, self).decode()
        self.src = [self.operands[0]]
        self.set_all_regs_touched()

    def execute(self):
        gv.fu.jump(self.operand_vals[0])


class CONDBRANCHInstruction(BRANCHInstruction):
    def decode(self):
        super(CONDBRANCHInstruction, self).decode()
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

        self.set_all_regs_touched()

    def execute(self):
        if self.operator(self.operand_vals[0], 0):
            gv.fu.jump(self.target)
            self.isTaken = True
            # gv.pipeline.pipe[Stages["DECODE"]] = getNOP() # here
        else:
            pass


class XORInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(XORInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

    def execute(self):
        self.result = self.operand_vals[0] ^ self.operand_vals[1]


class WRSInstruction(Instruction):
    def decode(self):
        super(WRSInstruction, self).decode()
        self.src = [int(self.operands[0])]
        self.result = ""
        self.set_all_regs_touched()

    def execute(self):
        while gv.data_mem[self.operand_vals[0]]:
            self.result += chr(gv.data_mem[self.operand_vals[0]])
            self.operand_vals[0] += 1

    def writeback(self):
        sys.stdout.write(self.result),
        sys.stdout.flush()


# STORE R5,R3,0 (src -> dest + offset)
class STOREInstruction(MEMInstruction):
    def decode(self):
        super(STOREInstruction, self).decode()
        self.src = list(self.operands)
        self.set_all_regs_touched()

    def execute(self):
        a = self.operand_vals[0]         & 0xFF
        b = (self.operand_vals[0] >> 8)  & 0xFF
        c = (self.operand_vals[0] >> 16) & 0xFF
        d = (self.operand_vals[0] >> 24) & 0xFF

        i0 = self.operand_vals[1] + self.operand_vals[2] + 0
        i1 = self.operand_vals[1] + self.operand_vals[2] + 1
        i2 = self.operand_vals[1] + self.operand_vals[2] + 2
        i3 = self.operand_vals[1] + self.operand_vals[2] + 3

        gv.data_mem[i0] = a
        gv.data_mem[i1] = b
        gv.data_mem[i2] = c
        gv.data_mem[i3] = d


# LOAD R5,R0,8 (src <- dest + offset)
class LOADInstruction(REGWRITEBACKInstruction, MEMInstruction):
    def decode(self):
        super(LOADInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

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
class LDIInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(LDIInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

    def execute(self):
        self.result = self.operand_vals[0]


# WR R5
class WRInstruction(Instruction):
    def decode(self):
        super(WRInstruction, self).decode()
        self.src = list(self.operands)
        self.set_all_regs_touched()

    def execute(self):
        self.result = str(self.operand_vals[0])

    def writeback(self):
        sys.stdout.write(self.result)
        sys.stdout.flush()

# SUBI R6,R1,0 (dest = src - imm) /// SUB R5,R2,R0 (dest = src1 - src2)
class SUBInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(SUBInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

    def execute(self):
        self.result = self.operand_vals[0] - self.operand_vals[1]


# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class ADDInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(ADDInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

    def execute(self):
        self.result = self.operand_vals[0] + self.operand_vals[1]


# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class MULInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(MULInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.set_all_regs_touched()

    def execute(self):
        self.result = self.operand_vals[0] * self.operand_vals[1]



# ADDI R6,R1,0 (dest = src + imm) /// ADD R6,R1,R2 (dest = src1 + src2)
class DIVInstruction(REGWRITEBACKInstruction):
    def decode(self):
        super(DIVInstruction, self).decode()
        self.dest = self.operands[0]
        self.src = list(self.operands[1:])
        self.duration = 3
        self.set_all_regs_touched()

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
