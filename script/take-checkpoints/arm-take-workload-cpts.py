import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
file_path = Path(__file__).resolve().parent

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
import gem5.utils.multisim as multisim
from script.boards.arm_board import *
from script.workloads.workloads import get_arm_npb_workload
import m5

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
class_size = "B"

multisim.set_num_processes(8)

def ignore_exit():
    while True:
        yield False

def workbegin_handler(benchmark):
    print(f"Taking checkpoint at workbegin for {benchmark}")
    print(f"Current tick: {m5.curTick()}")
    m5.checkpoint(Path(file_path/f"../workloads/checkpoints/{benchmark}-workbegin"))
    yield False

for bench in benchmarks:
    workload = get_arm_npb_workload(bench, class_size)
    board = get_KVM_board()
    board.set_workload(workload)
    multisim.add_simulator(
        Simulator(board=board,
                  on_exit_event={
                      ExitEvent.WORKBEGIN: workbegin_handler(bench),
                      ExitEvent.EXIT: ignore_exit()
                  },
                  id=f"arm-{bench}-{class_size}-workbegin-checkpoint")
    )

