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

from m5.objects import LooppointAnalysis, LooppointAnalysisManager, AddrRange

import m5

parser = argparse.ArgumentParser(description="Run the whole workload with detailed board")
parser.add_argument("--workload", help="The workload to run", required=True, type=str)
parser.add_argument("--process-map-info-json", help="The json file that contains the process map information", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
parser.add_argument("--output-dir", help="The directory to store the LoopPoint information", required=True, type=str)
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

output_path = Path(args.output_dir)
output_file = Path(output_path/f"{bench}-{class_size}-looppoint-analysis.json")

with open(output_file, "w") as f:
    json.dump({}, f)

manager = LooppointAnalysisManager()
manager.region_length = 800_000_000
all_trackers = []

with open(args.process_map_info_json) as f:
    workload_process_map_info = json.load(f)
workload_info = workload_process_map_info[bench]
source_address_range = workload_info["source_address_range"]
source_address_range = AddrRange(start=int(source_address_range[0],0), end=int(source_address_range[1],0))
restricted_address_ranges = workload_info["restricted_address_ranges"]
all_excluded_ranges = []
for restricted_address_range in restricted_address_ranges:
    all_excluded_ranges.append(AddrRange(start=int(restricted_address_range[0],0), end=int(restricted_address_range[1],0)))

for core in board.get_processor().get_cores():
    tracker = LooppointAnalysis()
    tracker.bb_valid_addr_range = AddrRange(0, 0)
    tracker.looppoint_analysis_manager = manager
    tracker.marker_valid_addr_range = source_address_range
    tracker.bb_excluded_addr_ranges = all_excluded_ranges
    core.core.probe_listener = tracker
    all_trackers.append(tracker)

board.set_workload(workload)

region_id = 0

def get_data():
    global region_id
    global manager
    global all_trackers
    global_bbv = manager.getGlobalBBV()
    global_bbv = to_hex_map(global_bbv)
    loop_counter = to_hex_map(manager.getBackwardBranchCounter())
    most_recent_loop = hex(manager.getMostRecentBackwardBranchPC())
    region_info = {
        "global_bbv" : global_bbv,
        "global_length" : manager.getGlobalInstCounter(),
        "global_loop_counter" : loop_counter,
        "most_recent_loop" : most_recent_loop,
        "most_recent_loop_count" : manager.getMostRecentBackwardBranchCount(),
        "bb_inst_map": to_hex_map(manager.getBBInstMap()),
        "locals" : []
    }
    for tracker in all_trackers:
        local_bbv = to_hex_map(tracker.getLocalBBV())
        region_info["locals"].append(local_bbv)
        tracker.clearLocalBBV()
    manager.clearGlobalBBV()
    manager.clearGlobalInstCounter()
    with open(output_file, "r") as f:
        data = json.load(f)
    data[region_id] = region_info
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    region_id += 1
    return region_id

def simpoint_handler():
    while True:
        current_region_id = get_data()
        print(f"Region {current_region_id-1} finished")
        yield False

def workend_handler():
    print("get to the end of the workload")
    current_region_id = get_data()
    print(f"Region {current_region_id-1} finished")
    yield True

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.SIMPOINT_BEGIN:simpoint_handler(),
        ExitEvent.WORKEND:workend_handler()
})

simulator.run()

print("Simulation finished!")
