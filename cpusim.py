#!/usr/bin/env python

import sys

def resolve_labels(program):
    label_targets = {}
    line_no = 0
    prev_line = ""
    same_line_no = []

    for line in program:
        line = line.strip()
        if ':' in line:
            same_line_no.append(line[:-1])
        else:
            if(same_line_no):
                for label in same_line_no:
                    label_targets[label] = line_no
            same_line_no = []
        line_no += 1
        prev_line = line

    for i in range(len(program)):
        instr = line = program[i].strip()

        if 'JMP' in instr:
            instr = "JMP " + str(label_targets[line.split(' ')[1]])
            print(line + " >"),
            print(instr)
            program[i] = instr

def main():
    input_filename = sys.argv[1]

    with open(input_filename, 'r') as ass_file:
        program = ass_file.readlines()

    resolve_labels(program)

if __name__ == '__main__':
    main()
