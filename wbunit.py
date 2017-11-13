import gv
from pipeline import *
import instruction
from collections import deque
import itertools

class WBUnit:
    def __init__(self, env):
        self.env = env
        self.last_instr = [instruction.getNOP()]
        gv.ROB = deque(maxlen=gv.ROB_entries)

    def do(self):
        # print("WB WILL WAIT")
        # wait for prev stage
        # print("WB", self.env.now)
        instr = gv.pipeline.pipe[Stages["WRITEBACK"]]

        # try:
        #     # print(list(itertools.islice(gv.ROB, 0, gv.retire_rate)))
        #     if gv.ROB[0] and gv.ROB[0].is_complete:
        #         robel = gv.ROB.popleft()
        #         print("From ROB, will WB", str(robel), instr, robel == instr)
        # except IndexError:
        #     pass

        self.writeback()
        if instr:
            self.last_instr = [instr]

        yield self.env.process(gv.pipeline.get_prev("WRITEBACK").do())

    def wait(self):
        # print("WB WAITING")
        # yield self.env.process(gv.pipeline.get_next("FETCH").wait())
        yield self.env.timeout(0)

    def writeback(self):
        # classic = True
        classic = False
        self.last_instr = [instruction.getNOP()]

        if classic:
            gv.unit_statuses[Stages["WRITEBACK"]] = "BUSY"

            instr = gv.pipeline.pipe[Stages["WRITEBACK"]]

            if instr:
                instr.writeback()
                gv.pipeline.pipe[Stages['WRITEBACK']] = None
                self.last_instr = [instr]

            gv.unit_statuses[Stages["WRITEBACK"]] = "READY"

        else:
            try:
                for i in range(gv.retire_rate):
                    if gv.ROB[0].is_complete:
                        instr = gv.ROB.popleft()
                        instr.writeback()
                        gv.pipeline.pipe[Stages['WRITEBACK']] = None
                        self.last_instr.append(instr)
                    else:
                        break
            except IndexError:
                pass # ROB empty
