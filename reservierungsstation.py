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
        mem_access_before_instr = False
        for x in self.shelved_instr:
            if x == instr:
                break
            if x.isMemAccess:
                mem_access_before_instr = True
                break

        # shelf test ok?
        #   s     s   Y
        #   s     d   N
        #   d     s   N
        #   d     d   N

        all_src_regs_free = gv.R.all_available(instr.get_src_regs(), instr)
        all_dest_regs_free = gv.R.all_available(instr.get_dest_regs(), instr)
        mem_access_in_flight = any(y.isMemAccess for y in self.instr_in_flight)

        gv.R.lock_regs(instr.get_all_regs_touched(), instr)
        instr.canDispatch = all_src_regs_free and all_dest_regs_free \
                            and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        # process instructions that have just completed
        # read bypassed data on bus, unlock dest regs
        for instr in list(self.instr_in_flight):
            if instr.isRetired:
                self.instr_in_flight.remove(instr)
                # potential performance enhancement
                # gv.R.unlock_regs(instr.get_reg_nums()["dest"], instr)
                gv.R.unlock_regs(instr.get_all_regs_touched(), instr)

        for eu in self.execUnits:
                if eu.status == "READY" and eu.instr: # finished and not processed
                    # get bypassed results
                    # potential performance enhancement
                    # gv.R.unlock_regs(instr.get_reg_nums()["src"], instr)
                    eu.instr = None # mark as processed

        for eu in self.execUnits:
            if eu.status == "READY":
                # check if any instr can go ahead, lock dest regs, dispatch it
                for instr in list(self.shelved_instr):
                    self.dispatch_check(instr)
                    if instr.canDispatch:
                        #dispatch
                        self.instr_in_flight.append(instr)
                        self.shelved_instr.remove(instr)
                        self.env.process(eu.do(instr))
                        break
                    else:
                        # print("Couldn't dispatch", self.shelved_instr[0])
                        pass

        yield self.env.timeout(1)

