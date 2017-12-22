R = None
pipeline = None
data_mem = []
unit_statuses = []
stages = []
instr_exec = 0
issue_rate = 4
ROB = None
ROB_entries = 32
retired = 0
retire_rate = issue_rate
wb = None
btb_wrong = 0
btb_all = 0

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

reg_renaming = False

print_trace = False
suppress_prog_stdout = False

br_pred = None
BTB_enabled = True

prediction_flavour = 1
nonpipelined = 0
pipelinedonly = 0
