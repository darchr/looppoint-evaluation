from m5.objects.DRAMInterface import DDR4_2400_16x4
from gem5.components.memory.memory import ChanneledMemory
from gem5.components.x86_board import X86Board
from gem5.components.cachehierarchies.ruby.mesi_three_level import MESIThreeLevelCacheHierarchy
from x86_board_components.sky_components.skylakeCPU import SkylakeCPU
from gem5.components.cache_hierarchies.classic.no_cache import NoCache
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes

def get_x86_board():
    processor = SkylakeCPU(num_cores=8)
    memory = ChanneledMemory(DDR4_2400_16x4, 2, 128, size="3GiB")
    cache = MESIThreeLevelCacheHierarchy(
        l1i_size="32KiB",
        l1i_assoc="8",
        l1d_size="32KiB",
        l1d_assoc="8",
        l2_size="256KiB",
        l2_assoc="8",
        l3_size="2MiB",
        l3_assoc="16",
        num_l3_banks=8,
    )
    system = X86Board(
        cache_hierarchy=cache,
        clk_freq="4GHz",
        processor=processor,
        memory=memory,
    )

    return system

def get_functional_board():
    processor = SimpleProcessor(
        cpu_type=CPUTypes.ATOMIC,
        isa=ISA.X86,
        num_cores=8
    )
    cache = NoCache()
    memory = ChanneledMemory(DDR4_2400_16x4, 1, 128, size="3GiB")
    system = X86Board(
        clk_freq="4GHz",
        processor=processor,
        cache_hierarchy=cache,
        memory=memory,
    )
    return system

def get_KVM_board():
    processor = SimpleProcessor(
        cpu_type=CPUTypes.KVM,
        isa=ISA.X86,
        num_cores=8
    )
    cache = NoCache()
    memory = ChanneledMemory(DDR4_2400_16x4, 1, 128, size="3GiB")
    system = X86Board(
        clk_freq="4GHz",
        processor=processor,
        cache_hierarchy=cache,
        memory=memory,
    )
    return system
