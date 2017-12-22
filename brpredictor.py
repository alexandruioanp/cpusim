import gv
from instruction import *

class BrPredictor:
    def __init__(self):
        self.btc = {}
        self.FIXED = 0
        self.STATIC = 1
        self.DYNAMIC = 2
        self.counters = {}

    def taken(self, instr):
        if isinstance(instr, JUMPInstruction):
            if gv.BTB_enabled:
                gv.btb_all += 1
                try:
                    instr.cachedTarget = self.btc[instr.pc]
                    instr.target = instr.cachedTarget
                    return True
                except KeyError:
                    instr.cachedTarget = -1
                    return False
            else:
                return False

        if gv.prediction_flavour == self.FIXED:
            prediction = True

        elif gv.prediction_flavour == self.STATIC:
            if instr.isUncondBranch:
                prediction = True
            else:
                if instr.pc < instr.target:
                    # forward branch not taken
                    prediction = False
                else:
                    # backward branch taken
                    prediction = True

        elif gv.prediction_flavour == self.DYNAMIC:
            try:
                cnt = self.counters[instr.pc]
                if cnt <= 1: # weakly not taken
                    prediction = False
                else:
                    prediction = True
            except KeyError:
                self.counters[instr.pc] = 0
                prediction = False

        if gv.debug_spec:
            print("predicting ", instr, "as", "taken" if prediction else "not taken")

        return prediction

    def update_counter(self, instr):
        if gv.prediction_flavour == self.DYNAMIC and not isinstance(instr, JUMPInstruction):
            if instr.isTaken:
                self.counters[instr.pc] = min(3, self.counters[instr.pc] + 1)
            else:
                self.counters[instr.pc] = max(0, self.counters[instr.pc] - 1)

    def cache_indirect_target(self, pc, target):
        self.btc[pc] = target
