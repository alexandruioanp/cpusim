import gv
from execunit import *
from registerfile import *
from pipeline import *
from collections import deque
from instruction import *

class Reservierungsstation:
    def __init__(self, env, num_eu):
        self.env = env
        self.num_eu = num_eu
        self.execUnits = []
        self.buffer_size = 16
        assert self.buffer_size < gv.ROB_entries
        self.shelved_instr = deque()
        self.status = "READY"
        self.result_bus = []

        for i in range(num_eu):
            self.execUnits.append(ExecUnit(self.env, i))

    def push(self, instr):
        if len(self.shelved_instr) < self.buffer_size: # can shelve more
            self.shelved_instr.append(instr)
            return 0
        else:
            return 1

    def dispatch_check(self, instr):
        # print(instr, "uses", instr.get_reg_nums())
        instr.canDispatch = gv.R.all_available(instr.get_reg_nums()["src"])

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        # process instructions that have just completed
        # read bypassed data on bus, unlock dest regs
        for eu in self.execUnits:
                if eu.status == "READY" and eu.instr: # finished and not processed
                    # get bypassed results
                    # print(eu.bypassed)
                    # unlock dest regs
                    gv.R.unlock_regs(eu.instr.get_reg_nums()["dest"])
                    eu.instr = None # mark as processed

        for eu in self.execUnits:
            if eu.status == "READY":
                # check if any instr can go ahead, lock dest regs, dispatch it
                for instr in list(self.shelved_instr):
                    self.dispatch_check(instr)
                    if instr.canDispatch:
                        # lock dest regs
                        gv.R.lock_regs(instr.get_reg_nums()["dest"])
                        #dispatch
                        self.shelved_instr.remove(instr)
                        self.env.process(eu.do(instr))
                        break
                    else:
                        # print("Couldn't dispatch", self.shelved_instr[0])
                        pass

        yield self.env.timeout(1)

