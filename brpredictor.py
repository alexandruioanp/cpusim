import gv

class BrPredictor:
    def __init__(self):
        pass

    def taken(self, instr):
        if instr.isUncondBranch:
            return True

        prediction = True
        if gv.debug_spec:
            print("predicting ", instr, "as", "taken" if prediction else "not taken")
        return prediction
