import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
print(str(Path(__file__).resolve().parent.parent.parent))

from script.boards.arm_board import *
from script.workloads.workloads import get_arm_npb_workload
from gem5.simulate.simulator import Simulator

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test-board", type=str, required=True,
    help="Name of the test board", choices=["KVM", "functional", "detailed"])
args = parser.parse_args()

board_type = args.test_board
workload = get_arm_npb_workload()

if board_type == "KVM":
    board = get_KVM_board()
elif board_type == "functional":
    board = get_functional_board()
    workload.set_parameter("checkpoint", Path("arm_checkpoint"))
    workload.set_parameter("readfile_contents", "./home/gem5/NPB3.4-OMP/MG/B/c_m5_fs_naive/aarch64/*.c_m5_fs_naive;")
elif board_type == "detailed":
    board = get_detailed_board()
else:
    raise ValueError("Invalid board type")

board.set_workload(workload)

sim = Simulator(board=board)
sim.run()
if board_type == "KVM":
    # sim.save_checkpoint("arm_checkpoint")
    while 1:
        sim.run()
elif board_type == "functional":
    sim.save_checkpoint("mg_checkpoint")
