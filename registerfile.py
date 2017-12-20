import gv
from collections import deque

class RegisterFile:
    def __init__(self, num_arch_reg = 32, num_phys_regs = 128):
        self.num_arch_reg = num_arch_reg
        self.num_phys_reg = num_phys_regs
        if not gv.reg_renaming:
            self._R = [0] * num_arch_reg
            self.available = [True] * num_arch_reg
            self.locked_by = [None] * num_arch_reg
        else:
            self._R = [0] * num_phys_regs
            self.free_tags = deque(range(101, 101 + num_phys_regs - 1))
            self.available = {}
            self.locked_by = {}

            self.remap_file = [-1] * num_arch_reg
            self.prev_remap_file = [-1] * num_arch_reg

            self.num_arch_reg = num_arch_reg
            self.all_tags_per_reg = []
            self.prev_all_tags_per_reg = []
            for i in range(num_arch_reg):
                self.all_tags_per_reg.append([])
                self.prev_all_tags_per_reg.append([])

            for i in range(100, 101 + num_phys_regs - 1):
                self.available[i] = True
                self.locked_by[i] = None


        self.tags_alloc = 0
        self.tags_dealloc = 0

        self.debug = True
        self.debug = False

    def speculate(self):
        if gv.reg_renaming:
            if self.debug:
                print("REG: SPECULATING. BACKING UP REMAP FILE")
                print("Remap file backup", self.remap_file)

            self.prev_remap_file = list(self.remap_file)
            self.prev_all_tags_per_reg = list(self.all_tags_per_reg)

            if self.debug:
                print("Backup is backup", self.prev_remap_file)

    def undoSpeculation(self):
        if gv.reg_renaming:
            if self.debug:
                print("REG: RESTORING REMAP FILE")
                print("BEFORE", self.remap_file)
            self.remap_file = list(self.prev_remap_file)
            self.prev_remap_file = [-1] * self.num_arch_reg

            self.all_tags_per_reg = list(self.prev_all_tags_per_reg)
            self.prev_all_tags_per_reg = []
            for i in range(self.num_arch_reg):
                self.prev_all_tags_per_reg.append([])

            if self.debug:
                print("AFTER restoring", self.remap_file)

    def get(self, reg):
        # if gv.reg_renaming and reg in self.free_tags:
        #     raise Exception("Reading from free tag", reg)

        if gv.reg_renaming:
            if gv.debug_ren:
                print("reading", reg, "(" + str(reg - 100) + ")", self._R[reg - 100])
            return self._R[reg - 100]
        else:
            return self._R[reg]

    def set(self, reg, val):
        # if gv.reg_renaming and reg in self.free_tags:
            # raise Exception("Writing to free tag", reg)

        if gv.reg_renaming:
            if self.debug:
                print("writing to", reg, "(" + str(reg-100) + ")", "value", val)
            self._R[reg - 100] = val
        else:
            if self.debug:
                print("writing to", reg, "value", val)
            self._R[reg] = val

    def release_tags(self, instr):
        # return
        if gv.debug_ren:
            print("Before freeing:", self.remap_file)
            # print("freed tags per arch reg", self.num_tags)

        for tag in instr._get_reg_nums()["dest"]:
            self.release_tag(tag)

        if gv.debug_ren:
            print("Freed some tags. FREE tags:", self.free_tags, "remap file", self.remap_file)
            # print("freed tags per arch reg", self.num_tags)

    def release_tag(self, tag):
        # return
        if tag == 100 or tag in self.free_tags:
            return
        self.tags_dealloc += 1

        should_remove = True

        for reg, tag_list in enumerate(self.all_tags_per_reg):
            if tag in tag_list:
                if gv.debug_ren:
                    print("IT IS", tag_list)
                if len(tag_list) == 1:
                    if gv.debug_ren:
                        print("@@@ last tag referring to reg", reg, "tag", tag, "l", tag_list)
                        print("All tags used", self.all_tags_per_reg)
                    should_remove = False

                if should_remove:
                    tag_list.remove(tag)
                break

        if should_remove:
            self.free_tags.append(tag)
            if gv.debug_ren:
                print("freed tag", tag)

        if self.debug:
            print("DEALLOC", self.tags_dealloc)

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
            tag = self.remap_file[src_reg]
            if tag == -1:
                if gv.debug_ren:
                    print("allocating new tag for", "R" + str(src_reg))

                old_tag = self.remap_file[src_reg]

                tag = self.get_new_free_tag(src_reg)
                if gv.debug_ren:
                    print("new tag is", tag, "overwriting", old_tag)

            if gv.debug_ren:
                print("tag for", src_reg, "is", self.remap_file[src_reg])

            new_src_regs.append(tag)

        if gv.debug_ren:
            print("DEST:")
        for dest_reg in dest_regs:
            if gv.debug_ren:
                print("allocating new tag for", "R" + str(dest_reg))
            # old_tag = self.remap_file[dest_reg]
            # if gv.debug_ren:
            #     print("removing old tag", old_tag)
            # self.release_tag(old_tag)
            old_tag = self.remap_file[dest_reg]
            tag = self.get_new_free_tag(dest_reg)
            if gv.debug_ren:
                print("new tag is", tag, "overwriting", old_tag)
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
            print("Used up some tags. FREE tags:", self.free_tags, "remap file", self.remap_file)

    def get_new_free_tag(self, reg):
        if reg == 0:
            return 100

        tag = self.free_tags.popleft()
        self.remap_file[reg] = tag
        self.all_tags_per_reg[reg].append(tag)

        if gv.debug_ren:
            print("new tag for", reg, "is", tag)
            print("REMAP FILE", self.remap_file)
            print("All tags used", self.all_tags_per_reg)

        self.tags_alloc += 1
        if self.debug:
            print("ALLOC", self.tags_alloc)

        return tag

    def reg_from_tag(self, tag):
        if gv.debug_ren:
            print("looking for tag", tag, "in", self.remap_file)
        for reg, remapped_tag in enumerate(self.remap_file):
            if remapped_tag == tag:
                return reg

        return -1

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
