#!/usr/bin/env python

import re
import argparse

from instruction import *
from fetchunit import *
from decunit import *
from wbunit import *
from registerfile import *
from pipeline import *
from reservierungsstation import *
import gv

debug = True
debug = False

class Computor:
    def __init__(self, program, env, clean_asm):
        self._program = program
        self.env = env
        self.fetchunit = FetchUnit(clean_asm, self.env)
        gv.fu = self.fetchunit
        self.decodeunit = DecUnit(self.env)
        self.wbunit = WBUnit(self.env)
        self.rs = Reservierungsstation(self.env, gv.issue_rate)
        gv.R = RegisterFile(48)
        self.clock_cnt = 0
        self.print_stats = False
        self.clean_asm = clean_asm
        gv.instr_exec = 0
        gv.stages = [self.fetchunit, self.decodeunit, self.rs]

    def run_simpy(self):
        while True:
            self.env.process(gv.pipeline.advance_yield())
            self.env.process(self.wbunit.do())  # W
            if self.rs.status == "READY":
                self.env.process(self.rs.do())  # RS
            if self.decodeunit.status == "READY":
                self.env.process(gv.stages[1].do())  # D
            self.env.process(gv.stages[0].do())  # F

            if gv.debug_timing:
                print("")
            #     print(str(self.env.now) + ": main ticking")

            # if self.wbunit.last_instr and self.wbunit.last_instr[-1].opcode == "HALT":
            #     break

            # print(self.wbunit.haltRetired)

            if self.wbunit.haltRetired:
                break

            yield self.env.timeout(1)
            # print(self.env.now)

        if self.print_stats:
            print("")
            print("*************************************")
            print("Cycles taken:", self.env.now)
            print("Instructions executed:", gv.instr_exec)
            print("Instructions retired:", gv.retired)
            print("IPC:", gv.retired / self.env.now)
            print("*************************************")
            print("Branches:", gv.num_branches)
            print("Mispredictions:", gv.mispred)


def assemble(asm, program, clean):
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

    pc = 0

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
            clean.append((line, pc))
            pc += 1


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
    gv.bypassing = args.bypass
    input_filename = args.file

    with open(input_filename, 'r') as ass_file:
        asm = ass_file.readlines()

    program = []
    clean_asm = []
    assemble(asm, program, clean_asm)

    # with open("tt.asm", 'w') as outf:
    #     for line in clean_asm:
    #         outf.write(str(line[1]) + '. ' + line[0])
    #         outf.write('\n')

    env = simpy.Environment()
    gv.pipeline = Pipeline(env)
    pc3000 = Computor(program, env, clean_asm)

    if args.stats:
        pc3000.print_stats = True

    gv.speculationEnabled = args.spec

    env.process(pc3000.run_simpy())
    env.run()

    # for i in clean_asm:
    #     if i:
    #         print(str(i[1]) + '.', i[0])

    # if debug:
        # print_data_mem()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Input .ass file')
    parser.add_argument('--simpy', required=False, default=1, type=int, choices={0, 1},
                        help='Run using simpy?')
    parser.add_argument('--stats', required=False, default=0, type=int, choices={0, 1},
                        help='Print run stats')
    parser.add_argument('--bypass', required=False, default=1, type=int, choices={0, 1},
                        help='Bypass results')
    parser.add_argument('--spec', required=False, default=1, type=int, choices={0, 1},
                        help='Speculative execution')

    args = parser.parse_args()

    main(args)
