#!/usr/bin/env python

import re
import argparse

import simpy

from instruction import *
from fetchunit import *
from decunit import *
from execunit import *
from wbunit import *
from registerfile import *
from pipeline import *
import gv

debug = True
debug = False

class Computor:
    def __init__(self, program, env=None):
        self._program = program
        self.env = env
        self.fetchunit = FetchUnit(program, self.env)
        gv.fu = self.fetchunit
        self.decodeunit = DecUnit(self.env)
        self.execunit = ExecUnit(self.env)
        self.wbunit = WBUnit(self.env)
        gv.R = RegisterFile(48)
        self.clock_cnt = 0
        self.print_stats = False
        gv.instr_exec = 0
        gv.stages = [self.fetchunit, self.decodeunit, self.execunit, self.wbunit]

    def run_simpy(self):

        events = []

        # events.append(self.env.process(gv.stages[3].do())) # W
        # events.append(self.env.process(gv.stages[2].do())) # E
        # events.append(self.env.process(gv.pipeline.advance_yield()))
        # events.append(self.env.process(gv.stages[1].do())) # F
        # events.append(self.env.process(gv.stages[0].do())) # D
        # events.append(self.env.process(gv.stages[3].do()))  # W
        # events.append(self.env.process(gv.stages[2].do()))  # E
        # events.append(self.env.process(gv.stages[1].do()))  # F
        # events.append(self.env.process(gv.stages[0].do()))  # D
        # events.append(self.env.process(gv.pipeline.advance_yield()))>

        while True:

            self.env.process(gv.pipeline.advance_yield())
            self.env.process(gv.stages[3].do())  # W
            if gv.unit_statuses[Stages["EXECUTE"]] == "READY":
                self.env.process(gv.stages[2].do())  # E
            self.env.process(gv.stages[1].do())  # F
            self.env.process(gv.stages[0].do())  # D

            if gv.debug_timing:
                print(str(self.env.now) + ": main ticking")

            if self.wbunit.last_instr[-1].opcode == "HALT":
                # for ev in events:
                #     ev.interrupt()
                # break
                break

            if self.env.now == 26:
                a = 3 + 2

            yield self.env.timeout(1)

        if self.print_stats:
            print("*************************************")
            print("Cycles taken:", self.env.now)
            print("Instructions executed:", gv.instr_exec)
            print("IPC:", gv.instr_exec / self.env.now)

def assemble(asm, program):
    label_targets = {}
    same_line_no = []
    addr = 0
    num_labels = 0

    for line_no in range(len(asm)):
        line = asm[line_no].strip()
        if ':' in line and "DATA" not in line:
            same_line_no.append(line[:-1])
        elif 'DATA' not in line:
            if same_line_no:
                num_labels += len(same_line_no)
                for label in same_line_no:
                    label_targets[label] = line_no - num_labels
            same_line_no = []

        else:
            gv.data_mem.append(int(re.search("\d+", line).group()))
            addr += 1

    for i in range(len(asm)):
        line = asm[i].strip()

        opcode = line.split(' ')[0]

        if opcode == 'JMP':
            line = "JMP " + str(label_targets[line.split(' ')[1]])

        if opcode in ['BGEZ', 'BNEZ', 'BLTZ', 'BEQZ']:
            operands = line.split(' ')[1]
            line = opcode + " " + operands .split(',')[0] + "," + str(label_targets[operands .split(',')[1]])

        if 'IADDR' in line:
            dest_reg, label = line.split(' ')[1].split(',')
            line = "LDI " + dest_reg + "," + str(label_targets[label])

        if 'DATA' not in line and ":" not in line:
            instr = get_instruction(line)
            program.append(instr)


def print_data_mem():
    # print("\n+    0 1 2 3"),
    print("")
    for idx, word in enumerate(gv.data_mem):
        print(idx, word)
        # if idx % 4 == 0:
        #     print "\n" + (str(idx) + ".").ljust(4),
        #
        # if word < 256:
        #     to_print = chr(word)
        #     print to_print if to_print.isalnum() else " ",
        # else:
        #     print word,


def main(args):
    input_filename = args.file

    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    assemble(asm, program)

    env = simpy.Environment()
    gv.pipeline = Pipeline(env)
    pc3000 = Computor(program, env)

    if args.stats:
        pc3000.print_stats = True

    env.process(pc3000.run_simpy())
    env.run()

    # if debug:
        # print_data_mem()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Input .ass file')
    parser.add_argument('--simpy', required=False, default=1, type=int, choices={0, 1},
                        help='Run using simpy?')
    parser.add_argument('--stats', required=False, default=0, type=int, choices={0, 1},
                        help='Print run stats')

    args = parser.parse_args()

    main(args)
