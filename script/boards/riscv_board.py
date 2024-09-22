from m5.objects.DRAMInterface import DDR4_2400_16x4
from gem5.components.memory.memory import ChanneledMemory
from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import MESITwoLevelCacheHierarchy
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes

def get_detailed_board():
    processor = SimpleProcessor(
        cpu_type=CPUTypes.O3,
        isa=ISA.RISCV,
        num_cores=8
    )
    memory = ChanneledMemory(DDR4_2400_16x4, 2, 128, size="8GiB")
    cache = MESITwoLevelCacheHierarchy(
        l1i_size="64KiB",
        l1i_assoc="8",
        l1d_size="64KiB",
        l1d_assoc="8",
        l2_size="1MiB",
        l2_assoc="64",
    )
    system = RiscvBoard(
        cache_hierarchy=cache,
        clk_freq="2GHz",
        processor=processor,
        memory=memory,
    )

    return system

def get_functional_board():
    processor = SimpleProcessor(
        cpu_type=CPUTypes.ATOMIC,
        isa=ISA.RISCV,
        num_cores=8
    )
    cache = NoCache()
    memory = ChanneledMemory(DDR4_2400_16x4, 1, 128, size="8GiB")
    system = RiscvBoard(
        clk_freq="2GHz",
        processor=processor,
        cache_hierarchy=cache,
        memory=memory,
    )
    return system
