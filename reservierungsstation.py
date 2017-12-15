import gv
from execunit import *
from registerfile import *
from pipeline import *
from collections import deque
from instruction import *

class Reservierungsstation:
    def __init__(self, env, eu_conf):
        self.env = env
        self.eu_conf = eu_conf
        self.avail_eu = dict(self.eu_conf)
        self.num_eu = 0

        for type in self.eu_conf.keys():
            self.num_eu += self.eu_conf[type]

        self.execUnits = []
        self.buffer_size = 16
        assert self.buffer_size < gv.ROB_entries
        self.shelved_instr = deque()
        self.status = "READY"
        self.result_bus = {-1: -1}
        self.instr_in_flight = []

        for i in range(self.num_eu):
            self.execUnits.append(ExecUnit(self.env, i, self.result_bus))

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

        gv.R.lock_regs(instr.get_all_regs_touched(), instr)

        if gv.bypassing:
            print("BYPASSSING")
            for r in instr.get_all_regs_touched():
                try:
                    print(instr, "deletes", "R" + str(r), self.result_bus["R" + str(r)])
                    del self.result_bus["R" + str(r)]
                    # print(self.result_bus)
                except KeyError:
                    print("key error")
                    pass

        all_src_regs_free = gv.R.all_available(instr.get_src_regs(), instr)
        which_locked = gv.R.which_locked(instr.get_src_regs(), instr)

        results_forwarded = True

        if which_locked:
            # print("Are locked:", which_locked, "asking", instr)
            # print(self.result_bus)
            for r in which_locked:
                if "R"+str(r) not in self.result_bus.keys():
                    results_forwarded = False
            # print("")

        all_dest_regs_free = gv.R.all_available(instr.get_dest_regs(), instr)
        mem_access_in_flight = any(y.isMemAccess for y in self.instr_in_flight)

        if gv.bypassing:
            which_locked = gv.R.which_locked(instr.get_src_regs(), instr)
            wlb = list(which_locked)

            results_forwarded = True

            if which_locked:
                # print("Are locked:", which_locked, "asking", instr)
                # print(self.result_bus)
                for r in list(which_locked):
                    if "R"+str(r) in self.result_bus.keys():
                        # print(r)
                        which_locked.remove(r)
                # print("")

            instr.canDispatch = (which_locked == []) and all_dest_regs_free \
                                and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))

            canDispatch2 = all_src_regs_free and all_dest_regs_free \
                           and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))

            for r in instr.get_dest_regs():
                try:
                    # print(instr, "deletes", "R" + str(r), self.result_bus["R" + str(r)])
                    del self.result_bus["R" + str(r)]
                    # print(self.result_bus)
                except KeyError:
                    pass
        else:
            instr.canDispatch = all_src_regs_free and all_dest_regs_free \
                and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr))

            if instr.canDispatch and instr.isSpeculative and instr.isStore:
                # print("WRONG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("WRONG????????????", instr.asm)

        assert not (instr.canDispatch and instr.isSpeculative and instr.isStore)

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        # process instructions that have just completed
        # read bypassed data on bus, regs
        # print("in flight (ret, mis, exec):", [(x.asm, x.isRetired, x.misspeculated, x.isExecuted) for x in self.instr_in_flight])
        for instr in list(self.instr_in_flight):
            if instr.isRetired or instr.misspeculated:
                self.instr_in_flight.remove(instr)
                gv.R.unlock_regs(instr.get_all_regs_touched(), instr)
            if  instr.misspeculated and gv.debug_spec:
                print("Misspeculated instr in flight", instr.asm)

        for instr in self.shelved_instr:
            gv.R.lock_regs(instr.get_all_regs_touched(), instr)

        for eu in self.execUnits:
                if eu.status == "READY" and eu.instr: # finished and not processed
                    if gv.bypassing:
                        # get bypassed results
                        if eu.bypassed:
                            (dest, val) = eu.bypassed
                            if dest:
                                self.result_bus[dest] = val
                    eu.instr = None # mark as processed

        for eu in self.execUnits:
            if eu.status == "READY":
                # check if any instr can go ahead, lock dest regs, dispatch it
                for instr in list(self.shelved_instr):
                    if instr.misspeculated:
                        if gv.debug_spec:
                            print("misspeculated instr on shelf", instr.asm)
                        self.shelved_instr.remove(instr)
                        gv.R.unlock_regs(instr.get_all_regs_touched(), instr)
                        continue

                    self.dispatch_check(instr)
                    if instr.canDispatch:
                        #dispatch
                        self.instr_in_flight.append(instr)
                        self.shelved_instr.remove(instr)

                        if gv.bypassing:
                            instr.evaluate_operands(self.result_bus)
                        else:
                            instr.evaluate_operands({})

                        self.env.process(eu.do(instr))

                        if gv.bypassing:
                            for r in instr.get_dest_regs():
                                try:
                                    del self.result_bus["R" + str(r)]
                                except KeyError:
                                    pass

                        break
                    else:
                        pass

        yield self.env.timeout(1)

