import global_vars
from pipeline import *

class Decoder:
    def __init__(self):
        pass

    def decode(self):
        instr = global_vars.pipeline.pipe[Stages["DECODE"]]
        if instr:
            instr.decode()