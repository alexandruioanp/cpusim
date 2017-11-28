import gv

class RegisterFile:
    def __init__(self, num_reg = 32):
        self._R = [0] * num_reg
        self.available = [True] * num_reg
        self.locked_by = [None] * num_reg

    def get(self, reg):
        return self._R[reg]

    def set(self, reg, val):
        self._R[reg] = val

    def lock_reg(self, reg, instr):
        if self.available[reg]:
            self.available[reg] = False
            self.locked_by[reg] = instr

    def lock_regs(self, lst, instr):
        for reg in lst:
            if reg != 0:
                self.lock_reg(reg, instr)

    def unlock_reg(self, reg, instr):
        if reg == 0: # R0 is hardwired to 0
            return

        # if self.available[reg]:
        #     raise Exception(str(instr) + " trying to unlock register " + str(reg) + " never locked")
        #
        # if self.locked_by[reg] and self.locked_by[reg] != instr:
        #     raise Exception(str(instr) + " trying to unlock register " + str(reg) +\
        #                     " locked by " + str(self.locked_by[reg]))

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

    def all_available(self, lst, instr):
        for r in lst:
            if not self.is_available(r, instr):
                return False

        return True
