#!/usr/bin/env python

import sys
import re

from instruction import *

R = [0] * 10


def run(program, data):
    for i in program:
        # print(i)
        if i:
            i.decode()
            i.execute()
            i.writeback()
        pass



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
        elif 'DATA' not in line:
            if same_line_no:
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
            # print(line)

        if 'DATA' not in line and ":" not in line and "HALT" not in line:
            instr = get_instruction(line)
            program.append(instr)


def main(input_filename):
    # sys.stdout = open("sim.out", "w")

    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    data_mem = []
    assemble(asm, program, data_mem)

    run(program, data_mem)

    # sys.stdout.close()


if __name__ == '__main__':
    # print(sys.argv)
    main(sys.argv[1])
