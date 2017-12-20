import gv
from instruction import *

class BrPredictor:
    def __init__(self):
        self.btc = {}
        pass

    def taken(self, instr):
        if instr.isUncondBranch:
            return True

        if isinstance(instr, JUMPInstruction):
            if gv.BTB_enabled:
                try:
                    instr.cachedTarget = self.btc[instr.pc]
                    instr.target = instr.cachedTarget
                    gv.btb_all += 1
                    return True
                except KeyError:
                    instr.cachedTarget = -1
                    return False
            else:
                return False

        # print(instr.pc, instr.target)

        if instr.pc < instr.target:
            # forward branch not taken
            prediction = False
        else:
            # backward branch taken
            prediction = True

        # prediction = True

        if gv.debug_spec:
            print("predicting ", instr, "as", "taken" if prediction else "not taken")

        return prediction

    def cache_indirect_target(self, pc, target):
        self.btc[pc] = target
