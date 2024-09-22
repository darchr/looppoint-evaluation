import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
print(str(Path(__file__).resolve().parent.parent.parent))

from script.boards.arm_board import *
from script.workloads.workloads import get_arm_npb_workload
from gem5.simulate.simulator import Simulator

board = get_KVM_board()
workload = get_arm_npb_workload("cg", "B")
board.set_workload(workload)

sim = Simulator(board=board)
while True:
    sim.run()
