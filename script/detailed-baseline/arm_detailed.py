from boards.arm_board import get_arm_board
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol
from gem5.resources.resource import (
        obtain_resource,
        Resource,
)
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--start-up-checkpoint-path", type=str, required=True,
    help="Path to the start-up checkpoint")
parser.add_argument("--workload-name", type=str, required=True,
    help="Name of the workload")
args = parser.parse_args("--worload-class", type=str, required=True,
    help="Class of the workload")

requires(isa=ISA.ARM, coherence_protocol=CoherenceProtocol.CHI)

board = get_arm_board()

cmd = "export OMP_NUM_THREADS=8;./home/gem5/NPB"

board.set_kernel_disk_workload(
    
)

# 
