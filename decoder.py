import gv
from pipeline import *

class Decoder:
    def decode(self):
        instr = gv.pipeline.pipe[Stages["DECODE"]]
        if instr:
            instr.decode()
