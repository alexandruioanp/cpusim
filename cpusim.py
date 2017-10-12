#!/usr/bin/env python

import re

from instruction import *
from fetchunit import *
from decoder import *
from execution_unit import *
from writeback_unit import *
from registerfile import *
from pipeline import *
import global_vars

class Computor:
    def __init__(self, program):
        self._program = program
        self.fetchunit = FetchUnit(program)
        self.decodeunit = Decoder()
        self.execunit = ExecUnit()
        self.wbunit = WBUnit()
        global_vars.R = RegisterFile(10)
        # self.decodeunit = dec
        # self.execunit = ex
        self.clock_cnt = 0

    def run(self):
        for i_list in self.fetchunit.fetch(1):
            for i in i_list:
                if i:
                    # fetch
                    self.clock_cnt += 1
                    global_vars.pipeline.push(i)

                    # print("START")
                    # print(global_vars.pipeline.pipe)
                    global_vars.pipeline.advance()
                    # decode
                    self.clock_cnt += 1
                    self.decodeunit.decode()
                    global_vars.pipeline.advance()
                    # print(global_vars.pipeline.pipe)
                    # execute
                    self.clock_cnt += 1
                    self.execunit.execute()
                    global_vars.pipeline.advance()
                    # print(global_vars.pipeline.pipe)
                    # writeback
                    self.clock_cnt += 1
                    self.wbunit.writeback()
                    # print("END")
                    # print(global_vars.pipeline.pipe)
                    # remove

        # print("Cycles taken:", self.clock_cnt)

def assemble(asm, program):
    label_targets = {}
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
            same_line_no = []

        else:
            global_vars.data_mem.append(int(re.search("\d+", line).group()))
            addr += 1

    for i in range(len(asm)):
        line = asm[i].strip()

        if 'JMP' in line:
            line = "JMP " + str(label_targets[line.split(' ')[1]])

        if 'IADDR' in line:
            dest_reg, label = line.split(' ')[1].split(',')
            line = "LDI " + dest_reg + "," + str(label_targets[label])

        if 'DATA' not in line and ":" not in line and 'HALT' not in line:
            instr = get_instruction(line)
            program.append(instr)


def main(input_filename):
    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    assemble(asm, program)

    global_vars.pipeline = Pipeline()
    pc3000 = Computor(program)

    pc3000.run()


if __name__ == '__main__':
    main(sys.argv[1])
