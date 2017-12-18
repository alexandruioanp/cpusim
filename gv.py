R = None
pipeline = None
data_mem = []
unit_statuses = []
stages = []
instr_exec = 0
issue_rate = 2
ROB = None
ROB_entries = 24
retired = 0
retire_rate = issue_rate
wb = None

num_branches = 0
mispred = 0
cond_br = 0

eu_conf = {
    "BRANCH": 1,
    "MEMORY": 1,
    "ALU": 4
}

bypassing = False

speculating = False
speculationEnabled = True
block_on_nested_speculation = True

debug_spec = False
debug_timing = False
debug_ren = False

reg_renaming = True

print_trace = False
suppress_prog_stdout = False
