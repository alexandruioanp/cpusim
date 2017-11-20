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
        #
        # shelved_dests = []
        # shelved_srcs = []
        # for x in self.shelved_instr:
        #     if x == instr:
        #         break
        #     shelved_dests.extend(x.get_reg_nums()["dest"])
        #     shelved_srcs.extend(x.get_reg_nums()["src"])
        #
        # in_flight_dests = []
        # in_flight_srcs = []
        # for x in self.instr_in_flight:
        #     if x == instr:
        #         break
        #     in_flight_dests.extend(x.get_reg_nums()["dest"])
        #     in_flight_srcs.extend(x.get_reg_nums()["src"])
        #
        mem_access_before_instr = False
        for x in self.shelved_instr:
            if x == instr:
                break
            if x.isMemAccess:
                mem_access_before_instr = True
                break
        #
        # # shelf test ok?
        # #   s     s   Y
        # #   s     d   N
        # #   d     s   N
        # #   d     d   N
        #
        # dependency_in_shelf = any(y in shelved_dests for y in instr.get_reg_nums()["src"]) or \
        #                       any(y in shelved_dests for y in instr.get_reg_nums()["dest"]) or \
        #                       any(y in shelved_srcs for y in instr.get_reg_nums()["dest"])
        #
        # dependency_in_flight = any(y in in_flight_dests for y in instr.get_reg_nums()["src"]) or \
        #                        any(y in in_flight_dests for y in instr.get_reg_nums()["dest"]) or \
        #                        any(y in in_flight_srcs for y in instr.get_reg_nums()["dest"])

        all_src_regs_free = gv.R.all_available(instr.get_reg_nums()["src"], instr)
        gv.R.lock_regs(instr.get_reg_nums()["dest"] + instr.get_reg_nums()["src"], instr)
        all_dest_regs_free = gv.R.all_available(instr.get_reg_nums()["dest"], instr)
        mem_access_in_flight = any(y.isMemAccess for y in self.instr_in_flight)

        # if instr.isMemAccess:
        #     print(instr, mem_access_in_flight, self.instr_in_flight)

        # instr.canDispatch = all_src_regs_free and not dependency_in_shelf and not dependency_in_flight \
        #                     and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))
        instr.canDispatch = all_src_regs_free and all_dest_regs_free \
                            and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        # process instructions that have just completed
        # read bypassed data on bus, unlock dest regs
        for instr in list(self.instr_in_flight):
            if instr.isRetired:
                self.instr_in_flight.remove(instr)
                # print("Unlocking", instr.get_reg_nums()["dest"], "from", instr)
                # gv.R.unlock_regs(instr.get_reg_nums()["dest"], instr)
                # gv.R.unlock_regs(instr.get_reg_nums()["src"], instr)

                gv.R.unlock_regs(instr.get_reg_nums()["dest"] + instr.get_reg_nums()["src"], instr)

        for eu in self.execUnits:
                if eu.status == "READY" and eu.instr: # finished and not processed
                    # get bypassed results
                    # print(eu.bypassed)
                    # unlock dest regs
                    eu.instr = None # mark as processed

        for eu in self.execUnits:
            if eu.status == "READY":
                # check if any instr can go ahead, lock dest regs, dispatch it
                for instr in list(self.shelved_instr):
                    self.dispatch_check(instr)
                    if instr.canDispatch:
                        # lock dest regs
                        # gv.R.lock_regs(instr.get_reg_nums()["dest"])
                        #dispatch
                        self.instr_in_flight.append(instr)
                        self.shelved_instr.remove(instr)
                        # gv.R.lock_regs(instr.get_reg_nums()["dest"], instr)
                        # gv.R.lock_regs(instr.get_reg_nums()["src"], instr)
                        gv.R.lock_regs(instr.get_reg_nums()["dest"] + instr.get_reg_nums()["src"], instr)
                        self.env.process(eu.do(instr))
                        break
                    else:
                        # print("Couldn't dispatch", self.shelved_instr[0])
                        pass

        yield self.env.timeout(1)

