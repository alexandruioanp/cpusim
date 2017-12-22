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
        self.buffer_size = 24
        # assert self.buffer_size < gv.ROB_entries
        self.shelved_instr = deque()
        self.status = "READY"
        self.result_bus = {-1: -1}
        self.instr_in_flight = []

        for i in range(self.num_eu):
            self.execUnits.append(ExecUnit(self.env, i, self.result_bus))

    def push(self, instr):
        if not self.is_full(): # can shelve more
            self.shelved_instr.append(instr)
            return 0
        else:
            return 1

    def is_full(self):
        return len(self.shelved_instr) >= self.buffer_size

    def dispatch_check(self, instr):
        if instr.isStore and instr.isSpeculative:
            instr.canDispatch = False
            return

        all_src_regs_free = gv.R.all_available(instr.get_unique_src_regs(), instr)
        all_dest_regs_free = gv.R.all_available(instr.get_unique_dest_regs(), instr)

        if not gv.bypassing and not (all_src_regs_free and all_dest_regs_free):
            instr.canDispatch = False
            return

        mem_access_before_instr = False
        for x in self.shelved_instr:
            if x == instr:
                break
            if x.isMemAccess:
                mem_access_before_instr = True
                break

        mem_access_in_flight = any(y.isMemAccess for y in self.instr_in_flight)

        if instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr):
            instr.canDispatch = False
            return

        # shelf test ok?
        #   s     s   Y
        #   s     d   N
        #   d     s   N
        #   d     d   N

        gv.R.lock_regs(instr.get_all_regs_touched(), instr)

        if gv.bypassing:
            # print("BYPASSSING")
            for r in instr.get_all_regs_touched():
                try:
                    # print(instr, "deletes", "R" + str(r), self.result_bus["R" + str(r)])
                    del self.result_bus["R" + str(r)]
                    # print(self.result_bus)
                except KeyError:
                    # print("key error")
                    pass


        if gv.bypassing:
            which_locked = gv.R.which_locked(instr.get_unique_src_regs(), instr)

            results_forwarded = True

            if which_locked:
                # print("Are locked:", which_locked, "asking", instr)
                # print(self.result_bus)
                for r in which_locked:
                    if "R"+str(r) not in self.result_bus.keys():
                        results_forwarded = False
                # print("")

        if gv.bypassing:
            which_locked = gv.R.which_locked(instr.get_unique_src_regs(), instr)
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

            for r in instr.get_unique_dest_regs():
                try:
                    # print(instr, "deletes", "R" + str(r), self.result_bus["R" + str(r)])
                    del self.result_bus["R" + str(r)]
                    # print(self.result_bus)
                except KeyError:
                    pass
        else:
            instr.canDispatch = all_src_regs_free and all_dest_regs_free \
                and not (instr.isMemAccess and (mem_access_in_flight or mem_access_before_instr)) \
                and not (instr.isStore and instr.isSpeculative)

            if instr.canDispatch and instr.isSpeculative and instr.isStore:
                print("WRONG????????????", instr.asm)

        # assert not (instr.canDispatch and instr.isSpeculative and instr.isStore)

    def lock_eu(self, instr):
        self.avail_eu[instr.type] -= 1
        assert self.avail_eu[instr.type] >= 0

    def release_eu(self, instr):
        self.avail_eu[instr.type] += 1
        if self.avail_eu[instr.type] > self.eu_conf[instr.type]:
            print(instr, self.avail_eu[instr.type], self.eu_conf[instr.type])
        assert self.avail_eu[instr.type] <= self.eu_conf[instr.type]

    def is_eu_avail(self, instr):
        return self.avail_eu[instr.type] > 0

    # check if instructions can go ahead, push them to available execution units
    def do(self):
        assert len(self.shelved_instr) <= self.buffer_size
        self.processRetiredInstructions()

        for instr in self.shelved_instr:
            gv.R.lock_regs(instr.get_all_regs_touched(), instr)

        self.cleanEUs()

        for eu in self.execUnits:
            if eu.status == "READY":
                for instr in list(self.shelved_instr):
                    if instr.misspeculated:
                        if gv.debug_spec:
                            print("misspeculated instr on shelf", instr.asm)
                        self.shelved_instr.remove(instr)
                        gv.R.unlock_regs(instr.get_all_regs_touched(), instr)
                        continue

                    self.dispatch_check(instr)

                    if instr.canDispatch and self.is_eu_avail(instr):
                        self.dispatch(instr, eu)
                        break

        yield self.env.timeout(1)

    def dispatch(self, instr, eu):
        assert not (instr.canDispatch and instr.isSpeculative and instr.isStore)
        if gv.debug_timing:
            print("dispatched", instr)
            print(instr, "locked EU:", self.avail_eu)

        self.lock_eu(instr)
        self.instr_in_flight.append(instr)
        self.shelved_instr.remove(instr)

        if gv.bypassing:
            instr.evaluate_operands(self.result_bus)
        else:
            instr.evaluate_operands({})

        if gv.debug_timing:
            print("RS dispatching", instr)

        self.env.process(eu.do(instr))

        # results on data bus no longer valid
        if gv.bypassing:
            for r in instr.get_unique_dest_regs():
                try:
                    del self.result_bus["R" + str(r)]
                except KeyError:
                    pass

    def processRetiredInstructions(self):
        for instr in list(self.instr_in_flight):
            # if gv.debug_timing:
            #     print("Processing", instr, "done?", instr.isRetired)
            if instr.isRetired or instr.misspeculated:
                self.instr_in_flight.remove(instr)
                gv.R.unlock_regs(instr.get_all_regs_touched(), instr)
                if gv.debug_timing:
                    print(instr, "unlocking regs:", instr.get_all_regs_touched())
            if instr.misspeculated and gv.debug_spec:
                print("Misspeculated instr in flight", instr.asm)

    # process instructions that have just completed
    def cleanEUs(self):
        for eu in self.execUnits:
            if eu.status == "READY" and eu.instr: # finished and not processed
                if gv.debug_timing:
                    print(eu.instr, "unlocking EU:", self.avail_eu, "ready", eu.instr.isExecuted)
                self.release_eu(eu.instr)
                # read bypassed data on bus, regs
                if gv.bypassing and eu.bypassed:
                    (dest, val) = eu.bypassed
                    if dest:
                        self.result_bus[dest] = val
                eu.instr = None # mark as processed

