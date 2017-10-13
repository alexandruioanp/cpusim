import sys

import global_vars

def get_instruction(line):
    opcode = line.split(' ')[0]

    try:
        i = instruction_types[opcode](line)
    except KeyError:
        i = ""

    return i

def getNOP():
    return NOPInstruction()

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
                        print("WILL REPLACE", "R" + str(reg), "with", val)
                    self.operand_vals.append(val)
                else:
                    if debug:
                        print("Will get from reg")
                    self.operand_vals.append(global_vars.R.get(int(src[1:])))

    def execute(self):
        pass

    def writeback(self):
        pass


class ALUInstruction(Instruction):
    def writeback(self):
        global_vars.R.set(int(self.dest[1:]), self.result)


class XORInstruction(ALUInstruction):
    def decode(self):
        # self.dest = int(self.operands[0][1:])
        self.dest = self.operands[0]
        # self.src = [int(self.operands[1][1:]), int(self.operands[2][1:])]
        # self.src = [int(self.operands[1][1:]), int(self.operands[2][1:])]
        self.src = list(self.operands[1:])

    def execute(self):
        self.result = self.operand_vals[0] ^ self.operand_vals[1]


class WRSInstruction(Instruction):
    def decode(self):
        self.src = [int(self.operands[0])]
        # self.src = list(self.operands)

    def execute(self):
        while global_vars.data_mem[self.operand_vals[0]]:
            sys.stdout.write(chr(global_vars.data_mem[self.operand_vals[0]])),
            self.operand_vals[0] += 1


class WRInstruction(Instruction):
    def decode(self):
        # self.src = [int(self.operands[0][1:])]
        self.src = list(self.operands)

    def execute(self):
        sys.stdout.write(str(self.operand_vals[0]))


class ADDIInstruction(ALUInstruction):
    def decode(self):
        self.dest = self.operands[0]
        # self.src = [int(self.operands[1][1:]), int(self.operands[2])]
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
        # "LDI": LDIInstruction,
        "NOP": NOPInstruction
    }
