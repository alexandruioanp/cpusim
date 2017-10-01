#!/usr/bin/env python

import sys
import re

class Instruction():
    def __str__(self):
        return self.opcode + " " + str(self.operands)

    def __init__(self, asm):
        comps = asm.split(' ')
        #if comps[0] == "HALT":
        #    self.opcode = comps[0]
        #    self.operands = [""]
        #else:
        self.opcode, self.operands = comps
        self.operands = self.operands.split(',')
        print(self.opcode, self.operands)

R = [0] * 10

def run(program, data):
    for i in program:
        if i.opcode == "XOR":
            dest = int(i.operands[0][1:])
            src1 = int(i.operands[1][1:])
            src2 = int(i.operands[2][1:])

            R[dest] = R[src1] ^ R[src2]
        elif i.opcode == "ADDI":
            dest = int(i.operands[0][1:])
            src = int(i.operands[1][1:])
            imm = int(i.operands[2])

            R[dest] = R[src] + imm
        elif i.opcode == "WR":
            src = int(i.operands[0][1:])
            sys.stdout.write(str(R[src]))
        elif i.opcode == "WRS":
            addr = int(i.operands[0])
            while data[addr]:
                sys.stdout.write(chr(data[addr])),
                addr += 1
        else:
            print("ERROR: unknown opcode", i.opcode)
            #sys.exit(1)

    print(R)

def assemble(asm, program, data):
    label_targets = {}
    line_no = 0
    prev_line = ""
    same_line_no = []

    addr = 0
    num_labels = 0

    for line_no in range(len(asm)):
        line = asm[line_no].strip()
        if ':' in line:
            same_line_no.append(line[:-1])
        elif not 'DATA' in line:
            if(same_line_no):
                num_labels += len(same_line_no)
                for label in same_line_no:
                    label_targets[label] = line_no - num_labels
                print(same_line_no, line_no - num_labels)
            same_line_no = []

        else:
            data.append(int(re.search("\d+", line).group()))
            addr += 1

    for i in range(len(asm)):
        line = asm[i].strip()

        if 'JMP' in line:
            line = "JMP " + str(label_targets[line.split(' ')[1]])

        if 'IADDR' in line:
            dest_reg, label = line.split(' ')[1].split(',')
            line = "LDI " + dest_reg + "," + str(label_targets[label])
            #print(line)

        if not 'DATA' in line and not ":" in line and not "HALT" in line:
            instr = Instruction(line)
            program.append(instr)

def main():
    input_filename = sys.argv[1]

    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    data_mem = []
    assemble(asm, program, data_mem)

    run(program, data_mem)

if __name__ == '__main__':
    main()
