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
        self.instr_in_flight = []

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
        all_src_regs_free = gv.R.all_available(instr.get_reg_nums()["src"])
        store_in_flight = False

        for i in self.instr_in_flight:
            if i.isStore:
                store_in_flight = True
                break

        store_before_load_on_shelf = False
        for x in self.shelved_instr:
            if x.isStore:
                store_before_load_on_shelf = True
            if x == instr:
                break

        load_bypassing_store = instr.isLoad and (store_in_flight or store_before_load_on_shelf)
        # if load_bypassing_store:
            # print("Load trying to bypass load", instr, self.instr_in_flight)

        shelved_dests = []
        for x in self.shelved_instr:
            if x != instr:
                shelved_dests.extend(x.get_reg_nums()["dest"])

        # print("Destinations in shelved instructions:", shelved_dests)

        dependency_in_shelf = any(x in shelved_dests for x in instr.get_reg_nums()["src"])

        instr.canDispatch = all_src_regs_free and not load_bypassing_store and not dependency_in_shelf

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        # process instructions that have just completed
        # read bypassed data on bus, unlock dest regs
        for eu in self.execUnits:
                if eu.status == "READY" and eu.instr: # finished and not processed
                    # get bypassed results
                    # print(eu.bypassed)
                    # unlock dest regs
                    self.instr_in_flight.remove(eu.instr)
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
                        self.instr_in_flight.append(instr)
                        self.shelved_instr.remove(instr)
                        self.env.process(eu.do(instr))
                        break
                    else:
                        # print("Couldn't dispatch", self.shelved_instr[0])
                        pass

        yield self.env.timeout(1)

