class RegisterFile:
    def __init__(self, num_reg = 20):
        self._R = [0] * num_reg

    def get(self, reg):
        return self._R[reg]

    def set(self, reg, val):
        self._R[reg] = val
