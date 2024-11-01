import sys
from pathlib import Path
import argparse
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
file_path = Path(__file__).resolve().parent

from script.utils import *

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol

from m5.objects import PcCountTracker, PcCountTrackerManager
from m5.params import PcCountPair

import shutil

import m5

parser = argparse.ArgumentParser(description="Run the whole workload with detailed board")
parser.add_argument("--workload", help="The workload to run", required=True, type=str)
parser.add_argument("--looppoint-info-json", help="The json file that contains the process map information", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
parser.add_argument("--output-dir", help="The directory to store the LoopPoint checkpoints", required=True, type=str)
args = parser.parse_args()

class_size = "B"
bench = args.workload

if args.arch == "arm":
    requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)
    from script.boards.arm_board import *
    from script.workloads.workloads import get_arm_npb_workload
    workload = get_arm_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_functional_board()
elif args.arch == "riscv":
    requires(isa_required=ISA.RISCV, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.riscv_board import *
    from script.workloads.workloads import get_riscv_npb_workload
    workload = get_riscv_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_functional_board()
elif args.arch == "x86":
    requires(isa_required=ISA.X86, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.x86_board import *
    from script.workloads.workloads import get_x86_npb_workload
    workload = get_x86_npb_workload(bench, class_size, start_from_workload_checkpoint=True)
    board = get_functional_board()

with open(args.looppoint_info_json, "r") as f:
    looppoint_info = json.load(f)
all_markers = looppoint_info[args.arch][bench]
region_marker_map = {}

target_pairs = set()

for rid, marker_info in all_markers.items():
    if marker_info["warmup_pc"] is not None:
        region_marker_map[PcCountPair(int(marker_info["warmup_pc"],0), int(marker_info["warmup_count"]))] = rid
        target_pairs.add(PcCountPair(int(marker_info["warmup_pc"],0), int(marker_info["warmup_count"])))
    elif marker_info["start_pc"] is not None:
        region_marker_map[PcCountPair(int(marker_info["start_pc"], 0), int(marker_info["start_count"]))] = rid
        target_pairs.add(PcCountPair(int(marker_info["start_pc"],0), int(marker_info["start_count"])))
    else:
        print(f"created cpt for region {rid}")
        shutil.copytree(workload.get_parameters()["checkpoint"], Path(f"{args.output_dir}/{bench}-{rid}-cpt"))

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

def convert_c_pc_count_pair_to_python(c_pc_count_pair):
    return PcCountPair(c_pc_count_pair.get_pc(), c_pc_count_pair.get_count())

def reached_marker():
    while True:
        print("reached marker")
        current_pc_count_pairs = convert_c_pc_count_pair_to_python(tracker_manager.getCurrentPcCountPair())
        print(current_pc_count_pairs)
        print(f"region id: {region_marker_map[current_pc_count_pairs]}")
        target_pairs.remove(current_pc_count_pairs)
        m5.checkpoint(Path(f"{args.output_dir}/{bench}-{region_marker_map[current_pc_count_pairs]}-cpt").as_posix())
        print(f"remaining targets: {len(target_pairs)}")
        if len(target_pairs) == 0:
            print("All markers reached")
            yield True
        else:
            yield False

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.SIMPOINT_BEGIN:reached_marker(),
})

simulator.run()

print("Simulation finished!")
