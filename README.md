# cpusim
Python-based CPU simulator written for the 4th year Advanced Computer Architecture course at the University of Bristol

### !!! The most up-to-date branch is `simpy`. Make sure to check it out before trying anything. !!!

To run, you need the [simpy discrete-event simulation framework](https://simpy.readthedocs.io/en/latest/).

Example programs are provided in `tests`. Each subfolder contains the original source file, the compiled version, and the expected output. The simulator includes an assembler, and the input file is an assembly file (`.ass`). Any data needed is preloaded into memory and included in the assembly file.

All of the working features are enabled by default, so you can simply run e.g. `python cpusim.py --file tests/functions10/functions10.ass`.
Example output (with `--stats 1`):
```
λ python cpusim.py --file tests\qsort\qsort10.ass --stats 1
quicksort. Enter n: Enter 10 numbers:
Unsorted array: 16777316, 1826, 3, 2337, 45, 2564, 10, 335395, 813, 0
Sorted array: 0, 3, 10, 45, 813, 1826, 2337, 2564, 335395, 16777316

*************************************
Cycles taken: 1662
Instructions executed: 1911
Instructions retired: 1763
IPC: 1.06
*************************************
Conditional branches: 160 Total branches: 267
Correct:              99 | 61.88%
Total BTB accesses: 19
BTB wrong:       8 | 42.11%
```

Run `python cpusim.py -h` for more info.

Features:
- Five-stage pipeline with a unified reservation station
- Superscalar
- Out-of-order execution (reorder buffer)
- Branch prediciton & speculative execution (depth of 1)
- Branch target buffer/branch target access cache


Supported instructions:
- XOR
- HALT
- WRS
- STORE
- BGEZ
- BLTZ
- BEQZ
- BNEZ
- JMP (label)
- JUMP (reg)
- LOAD
- LDI
- IADDR
- ADDI
- SUBI
- MULI
- DIVI
- ADD
- SUB
- MUL
- DIV
