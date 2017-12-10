import gv

class BrPredictor:
    def __init__(self):
        pass

    def taken(self, instr):
        prediction = True
        if gv.debug_spec:
            print("predicting ", instr, "as", "taken" if prediction else "not taken")
        return prediction
