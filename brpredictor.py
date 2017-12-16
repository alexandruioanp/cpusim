import gv
from instruction import *

class BrPredictor:
    def __init__(self):
        pass

    def taken(self, instr):
        if instr.isUncondBranch:
            return True

        if isinstance(instr, JUMPInstruction):
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
