#!/usr/bin/env python

import sys

def main():
    input_filename = sys.argv[1]

    with open(input_filename, 'r') as ass_file:
        program = ass_file.readlines()

if __name__ == '__main__':
    main()
