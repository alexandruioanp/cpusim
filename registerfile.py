import gv
from collections import deque

class RegisterFile:
    def __init__(self, num_reg = 32, num_phys_regs = 64):
        if not gv.reg_renaming:
            self._R = [0] * num_reg
            self.available = [True] * num_reg
            self.locked_by = [None] * num_reg
        else:
            self._R = [0] * num_phys_regs
            self.free_tags = deque(range(101, 101 + num_phys_regs - 1))
            self.available = {}
            self.locked_by = {}

            self.remap_file = {}
            self.prev_remap_file = {}
            self.remap_count = {}

            for i in range(100, 101 + num_phys_regs - 1):
                self.available[i] = True
                self.locked_by[i] = None

            self.num_tags = [0] * num_reg

        self.tags_alloc = 0
        self.tags_dealloc = 0

        self.debug = True
        self.debug = False

    def speculate(self):
        if self.debug:
            print("REG: SPECULATING. BACKING UP REMAP FILE")
            print("Remap file backup", self.remap_file)
        self.prev_remap_file = dict(self.remap_file)

    def undoSpeculation(self):
        if self.debug:
            print("REG: RESTORING REMAP FILE")
            print("BEFORE", self.remap_file)
        self.remap_file = dict(self.prev_remap_file)
        self.prev_remap_file = {}

        if self.debug:
            print("AFTER restoring", self.remap_file)

    def get(self, reg):
        if gv.reg_renaming:
            if gv.debug_ren:
                print("reading", reg, "(" + str(reg - 100) + ")", self._R[reg - 100])
            return self._R[reg - 100]
        else:
            return self._R[reg]

    def set(self, reg, val):
        if gv.reg_renaming and reg in self.free_tags:
            raise Exception("Writing to free tag", reg)

        if gv.reg_renaming:
            if self.debug:
                print("writing to", reg, "(" + str(reg-100) + ")", "value", val)
            self._R[reg - 100] = val
        else:
            if self.debug:
                print("writing to", reg, "value", val)
            self._R[reg] = val

    def release_tags(self, instr):
        for tag in instr._get_reg_nums()["dest"]:
            if tag == 100:
                continue
            self.free_tags.append(tag)
            self.tags_dealloc += 1
            if self.debug:
                print("DEALLOC", self.tags_dealloc)

        if gv.debug_ren:
            print("Freed some tags. FREE tags:", self.free_tags)
            print("freed tags per arch reg", self.num_tags)

    def rename(self, instr):
        src_regs = instr._get_reg_nums()["src"]
        dest_regs = instr._get_reg_nums()["dest"]
        if gv.debug_ren:
            print("before renaming", instr.asm, "src", src_regs, "dest", dest_regs, "all", instr.get_all_regs_touched())

        new_src_regs = []
        new_dest_regs = []

        if gv.debug_ren:
            print("SRC:")

        for src_reg in src_regs:
            try:
                tag = self.remap_file[src_reg]
                if gv.debug_ren:
                    print("tag for", src_reg, "is", self.remap_file[src_reg])
            except KeyError:
                if gv.debug_ren:
                    print("allocating new tag for", src_reg)
                tag = self.get_new_free_tag(src_reg)
                if gv.debug_ren:
                    print("new tag is", tag)

            new_src_regs.append(tag)

        if gv.debug_ren:
            print("DEST:")
        for dest_reg in dest_regs:
            if gv.debug_ren:
                print("allocating new tag for", dest_reg)
            tag = self.get_new_free_tag(dest_reg)
            if gv.debug_ren:
                print("new tag is", tag)
            new_dest_regs.append(tag)

        instr.set_renamed_regs(new_src_regs, new_dest_regs)

        if gv.debug_ren:
            print("setting to", new_src_regs, new_dest_regs)
            src_regs = instr._get_reg_nums()["src"]
            dest_regs = instr._get_reg_nums()["dest"]
            if gv.debug_ren:
                print("after renaming", instr.asm, "src", src_regs, "dest", dest_regs, "all", instr.get_all_regs_touched())
            print("")

        if gv.debug_ren:
            print("Used up some tags. FREE tags:", self.free_tags)

    def get_new_free_tag(self, reg):
        if reg == 0:
            return 100

        tag = self.free_tags.popleft()
        self.remap_file[reg] = tag

        if gv.debug_ren:
            print("REMAP FILE", self.remap_file)

        self.tags_alloc += 1
        self.num_tags[reg] += 1
        if self.debug:
            print("ALLOC", self.tags_alloc)
            print("allocated tags per arch reg", self.num_tags)

        return tag

    def lock_reg(self, reg, instr):
        if self.available[reg]:
            if self.debug:
                print(instr, "locking", reg)
            self.available[reg] = False
            self.locked_by[reg] = instr

    def lock_regs(self, lst, instr):
        for reg in lst:
            if reg != 0 and reg != 100:
                self.lock_reg(reg, instr)

    def unlock_reg(self, reg, instr):
        if reg == 0 or reg == 100: # R0 is hardwired to 0
            return

        # if self.available[reg]:
        #     raise Exception(str(instr) + " trying to unlock register " + str(reg) + " never locked")
        #
        # if self.locked_by[reg] and self.locked_by[reg] != instr:
        #     raise Exception(str(instr) + " trying to unlock register " + str(reg) +\
        #                     " locked by " + str(self.locked_by[reg]))

        if self.debug:
            print(instr.asm, "unlocking", reg)

        self.available[reg] = True
        self.locked_by[reg] = None

    def unlock_regs(self, lst, instr):
        for reg in lst:
            self.unlock_reg(reg, instr)

    def is_available(self, reg, instr):
        return self.available[reg] or self.locked_by[reg] == instr

    def which_locked(self, lst, instr):
        out = []

        # filter
        for reg in lst:
            if not self.is_available(reg, instr):
                out.append(reg)

        return out

    def who_locked(self, reg):
        return self.locked_by[reg]

    def all_available(self, lst, instr):
        for r in lst:
            if not self.is_available(r, instr):
                return False

        return True
