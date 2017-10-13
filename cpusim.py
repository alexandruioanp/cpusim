#!/usr/bin/env python

import re
import argparse

from instruction import *
from fetchunit import *
from decoder import *
from execution_unit import *
from writeback_unit import *
from registerfile import *
from pipeline import *
import global_vars

debug = True
debug = False

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

    def run_non_pipelined(self):
        for i_list in self.fetchunit.fetch(1):
            if debug:
                print("START")

            # fetch
            if debug:
                print(global_vars.pipeline.pipe, "clk", self.clock_cnt)
            global_vars.pipeline.push(i_list[0])
            global_vars.pipeline.advance()
            self.clock_cnt += 1

            #decode
            if debug:
                print("After fetch:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.decodeunit.decode()
            global_vars.pipeline.advance()
            self.clock_cnt += 1

            # execute
            if debug:
                print("After decode:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.execunit.execute()
            global_vars.pipeline.advance()
            self.clock_cnt += 1

            # writeback
            if debug:
                print("After execute:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.wbunit.writeback()
            global_vars.pipeline.advance()
            self.clock_cnt += 1

            if debug:
                print("After writeback:", global_vars.pipeline.pipe, "clk", self.clock_cnt)

            if debug:
                print("END")

        # print("Cycles taken:", self.clock_cnt)


    def run_pipelined(self):
        for i_list in self.fetchunit.fetch(1):
            # fetch
            if debug:
                print("START")

            # fetch
            if debug:
                print(global_vars.pipeline.pipe, "clk", self.clock_cnt)
            global_vars.pipeline.push(i_list[0])
            self.clock_cnt += 1

            #decode
            if debug:
                print("After fetch:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.decodeunit.decode()

            # execute
            if debug:
                print("After decode:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.execunit.execute()

            # writeback
            if debug:
                print("After execute:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
            self.wbunit.writeback()
            global_vars.pipeline.advance()

            if debug:
                print("After writeback:", global_vars.pipeline.pipe, "clk", self.clock_cnt)

            if debug:
                print("END")

        #
        self.decodeunit.decode()
        self.execunit.execute()
        if debug:
            print("Before flush 1:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
        self.wbunit.writeback()
        self.clock_cnt += 1

        #
        global_vars.pipeline.advance()
        self.decodeunit.decode()
        self.execunit.execute()
        if debug:
            print("Before lush 2:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
        self.wbunit.writeback()
        self.clock_cnt += 1

        #
        global_vars.pipeline.advance()
        self.decodeunit.decode()
        self.execunit.execute()
        if debug:
            print("Before flush 3:", global_vars.pipeline.pipe, "clk", self.clock_cnt)
        self.wbunit.writeback()
        self.clock_cnt += 1

        if debug:
            print("After flush 3:", global_vars.pipeline.pipe, "clk", self.clock_cnt)

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


def main(args):
    input_filename = args.file

    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    assemble(asm, program)

    global_vars.pipeline = Pipeline()
    pc3000 = Computor(program)

    pc3000.run_pipelined() if args.pipelined else pc3000.run_non_pipelined()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Input .ass file')
    parser.add_argument('--pipelined', required=False, default=0, type=int, choices={0, 1}, help='Run in pipelined mode?')

    args = parser.parse_args()

    main(args)
