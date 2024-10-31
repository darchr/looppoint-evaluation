import sys
from pathlib import Path
import argparse

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
file_path = Path(__file__).resolve().parent

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol

import m5

parser = argparse.ArgumentParser(description="Run the whole workload with detailed board")
parser.add_argument("--workload", help="The workload to run", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
args = parser.parse_args()

class_size = "B"
bench = args.workload

if args.arch == "arm":
    requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)
    from script.boards.arm_board import *
    from script.workloads.workloads import get_arm_npb_workload
    workload = get_arm_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_detailed_board()
elif args.arch == "riscv":
    requires(isa_required=ISA.RISCV, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.riscv_board import *
    from script.workloads.workloads import get_riscv_npb_workload
    workload = get_riscv_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_detailed_board()
elif args.arch == "x86":
    requires(isa_required=ISA.X86, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.x86_board import *
    from script.workloads.workloads import get_x86_npb_workload
    workload = get_x86_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_detailed_board()

max_tick = 1000_000_000_000

def handle_workend():
    print(f"Encounter workend event, dump the stats. Current ticks: {m5.curTick()}.")
    m5.stats.dump()
    yield False

def handle_max_tick():
    print(f"Encounter max tick event, dump the stats. Current ticks: {m5.curTick()}.")
    m5.stats.dump()
    yield False

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKEND:handle_workend(),
        ExitEvent.MAX_TICK:handle_max_tick()
}
)

simulator.run(max_tick)

print("Simulation finished!")
