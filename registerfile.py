class RegisterFile:
    def __init__(self, num_reg = 32):
        self._R = [0] * num_reg
        self.available = [True] * num_reg

    def get(self, reg):
        return self._R[reg]

    def set(self, reg, val):
        self._R[reg] = val

    def lock_reg(self, reg):
        self.available[int(reg)] = False

    def lock_regs(self, lst):
        for reg in lst:
            self.lock_reg(reg)

    def unlock_reg(self, reg):
        self.available[int(reg)] = True

    def unlock_regs(self, lst):
        for reg in lst:
            self.unlock_reg(reg)

    def is_available(self, reg):
        return self.available[int(reg)]

    def all_available(self, lst):
        return all(map(self.is_available, lst))
