from m5.util import inform

from gem5.isas import ISA
from gem5.runtime import get_supported_isas

if ISA.ARM in get_supported_isas():
    from .full_system_arm_board import FullSystemArmBoard
else:
    inform(
        "gem5 build does not have ARM ISA support. "
        "Skipping FullSystemArmBoard import in components.boards."
    )
from .synth_traffic_board import SynthTrafficBoard
from .syscall_emulation_board import SyscallEmulationBoard
