import sys
from pathlib import Path
import argparse
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
file_path = Path(__file__).resolve().parent

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol

from m5.objects import PcCountTracker, PcCountTrackerManager
from m5.params import PcCountPair

import m5

parser = argparse.ArgumentParser(description="Run the whole workload with detailed board")
parser.add_argument("--workload", help="The workload to run", required=True, type=str)
parser.add_argument("--looppoint-info-json", help="The json file that contains the process map information", required=True, type=str)
parser.add_argument("--rid", help="The region id to restore", required=True, type=int)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
args = parser.parse_args()

class_size = "B"
bench = args.workload
rid = args.rid

if args.arch == "arm":
    requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)
    from script.boards.arm_board import *
    from script.workloads.workloads import get_arm_npb_workload
    workload = get_arm_npb_workload(bench, class_size, start_from_rid_checkpoint=rid)
    board = get_detailed_board()
elif args.arch == "riscv":
    requires(isa_required=ISA.RISCV, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.riscv_board import *
    from script.workloads.workloads import get_riscv_npb_workload
    workload = get_riscv_npb_workload(bench, class_size, start_from_rid_checkpoint=rid)
    board = get_detailed_board()
elif args.arch == "x86":
    requires(isa_required=ISA.X86, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.x86_board import *
    from script.workloads.workloads import get_x86_npb_workload
    workload = get_x86_npb_workload(bench, class_size, start_from_rid_checkpoint=rid)
    board = get_detailed_board()

with open(args.looppoint_info_json, "r") as f:
    looppoint_info = json.load(f)
rid_markers = looppoint_info[args.arch][bench][str(rid)]

marker_map = {}
target_pairs = set()

if rid_markers["warmup_pc"] is not None:
    marker_map[PcCountPair(int(rid_markers["start_pc"],0), int(rid_markers["start_count"]))] = "start marker"
    target_pairs.add(PcCountPair(int(rid_markers["start_pc"],0), int(rid_markers["start_count"])))
marker_map[PcCountPair(int(rid_markers["end_pc"], 0), int(rid_markers["end_count"]))] = "end marker"
target_pairs.add(PcCountPair(int(rid_markers["end_pc"],0), int(rid_markers["end_count"])))

print("all targets:")
for target in target_pairs:
    print(target)

tracker_manager = PcCountTrackerManager()
tracker_manager.targets = list(target_pairs)

all_trackers = []

for core in board.get_processor().get_cores():
    tracker = PcCountTracker()
    tracker.targets = list(target_pairs)
    tracker.ptmanager  = tracker_manager
    tracker.core = core.core
    core.core.probe_listener = tracker
    all_trackers.append(tracker)

def handle_workend():
    print(f"Encounter workend event, dump the stats. Current ticks: {m5.curTick()}.")
    m5.stats.dump()
    yield False

def convert_c_pc_count_pair_to_python(c_pc_count_pair):
    return PcCountPair(c_pc_count_pair.get_pc(), c_pc_count_pair.get_count())

def reached_marker():
    while True:
        print("reached marker")
        current_pc_count_pairs = convert_c_pc_count_pair_to_python(tracker_manager.getCurrentPcCountPair())
        print(current_pc_count_pairs)
        marker_type = marker_map[current_pc_count_pairs]
        print(f"marker type: {marker_type}")
        target_pairs.remove(current_pc_count_pairs)
        if marker_type == "end marker":
            print("All markers reached")
            yield True
        else:
            print("Dump and reset stats")
            m5.stats.dump()
            m5.stats.reset()
            yield False

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKEND:handle_workend(),
        ExitEvent.SIMPOINT_BEGIN:reached_marker(),
}
)

simulator.run()

print("Simulation finished!")
