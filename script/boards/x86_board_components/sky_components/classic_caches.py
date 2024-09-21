
#Authors: Mahyar Samani, Mitha Mysore, Alyssa Vallejo

from typing import Type, Optional

from m5.objects import (
    BadAddr,
    BasePrefetcher,
    BaseXBar,
    Cache,
    L2XBar,
    Port,
    Prefetcher,
    StridePrefetcher,
    SystemXBar,
)

from m5.params import NULL

from gem5.isas import ISA
from gem5.utils.override import overrides
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.abstract_cache_hierarchy import (
    AbstractCacheHierarchy,
)
from gem5.components.cachehierarchies.abstract_three_level_cache_hierarchy import (
    AbstractThreeLevelCacheHierarchy,
)
from gem5.components.cachehierarchies.classic.abstract_classic_cache_hierarchy import (
    AbstractClassicCacheHierarchy,
)
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache

class ClassicThreeLevelCache(
    AbstractClassicCacheHierarchy, AbstractThreeLevelCacheHierarchy
):
    """
    A cache setup where each core has a private L1 Data and Instruction Cache,
    and a private L2 cache.
    """

    @staticmethod
    def _get_default_membus() -> SystemXBar:
        """
        A method used to obtain the default memory bus of 64 bit in width for
        the PrivateL1PrivateL2 CacheHierarchy.

        :returns: The default memory bus for the PrivateL1PrivateL2
                  CacheHierarchy.

        """
        membus = SystemXBar(width=64) #Do not change
        membus.badaddr_responder = BadAddr()
        membus.default = membus.badaddr_responder.pio
        return membus

    def __init__(
        self,
        l1d_size: str = "32KiB",
        l1d_assoc: int = 8,      
        l1i_size: str = "32KiB",
        l1i_assoc: int = 8,
        l2_size: str = "256KiB",
        l2_assoc: int = 4,
        l3_size: str = "2MiB",
        l3_assoc: int = 16,
        membus: BaseXBar = _get_default_membus.__func__(),
        general_prefetcher: Type[BasePrefetcher] = StridePrefetcher,
        l1d_prefetcher: Optional[Type[BasePrefetcher]] = None,
        l1i_prefetcher: Optional[Type[BasePrefetcher]] = None,
        l2_prefetcher: Optional[Type[BasePrefetcher]] = None,
        l3_prefetcher: Optional[Type[BasePrefetcher]] = None,
    ) -> None:
        
        # @param:
        # general_prefetcher: Prefetcher for all caches with unless another prefetcher is specified
        # l1d_prefetcher: Overrides general_prefetcher for l1d_cache
        # l1i_prefetcher: Overrides general_prefetcher for l1i_cache
        # l12_prefetcher: Overrides general_prefetcher for l12_cache
        # l13_prefetcher: Overrides general_prefetcher for l13_cache
        # Example:
        #   If general_prefetcher is StridePrefetcher and only l2_prefetcher is set to NULL
        #   (e.g. You set
        #       cache_hierarchy = ClassicThreeLevelCache(general_prefetcher=StridePrefetcher, l2_prefetcher=NULL)),
        #       then in theory,
        #           l1d_prefetcher = StridePrefetcher
        #           l1i_prefetcher = StridePrefetcher
        #           l2_prefetcher = NULL
        #           l3_prefetcher = StridePrefetcher
        #       (This is implemented differently in the code)

        AbstractClassicCacheHierarchy.__init__(self=self)
        AbstractThreeLevelCacheHierarchy.__init__(
            self,
            l1i_size=l1i_size,
            l1i_assoc=l1i_assoc,
            l1d_size=l1d_size,
            l1d_assoc=l1d_assoc,
            l2_size=l2_size,
            l2_assoc=l2_assoc,
            l3_size=l3_size,
            l3_assoc=l3_assoc,
        )

        self.membus = membus
        self._general_prefetcher = general_prefetcher
        self._l1d_prefetcher = l1d_prefetcher
        self._l1i_prefetcher = l1i_prefetcher
        self._l2_prefetcher = l2_prefetcher
        self._l3_prefetcher = l3_prefetcher
    

    @overrides(AbstractClassicCacheHierarchy)
    def get_mem_side_port(self) -> Port:
        return self.membus.mem_side_ports

    @overrides(AbstractClassicCacheHierarchy)
    def get_cpu_side_port(self) -> Port:
        return self.membus.cpu_side_ports
    
    @overrides(AbstractCacheHierarchy)
    def incorporate_cache(self, board: AbstractBoard) -> None:
        # Set up the system port for functional access from the simulator.
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_memory().get_mem_ports():
            self.membus.mem_side_ports = port
            
        # Set up L1I Caches
        l1icaches = []
        for _ in range(board.get_processor().get_num_cores()):
            if self._l1i_prefetcher == None:
                l1icaches.append(ThisL1ICache(prefetcher=self._general_prefetcher()))
            else:
                l1icaches.append(ThisL1ICache(prefetcher=self._l1i_prefetcher()))
        
        self.l1icaches = l1icaches
        
        # Set up L1D Caches
        l1dcaches = []
        for _ in range(board.get_processor().get_num_cores()):
            if self._l1d_prefetcher == None:
                l1dcaches.append(ThisL1DCache(prefetcher=self._general_prefetcher()))
            else:
                l1dcaches.append(ThisL1DCache(prefetcher=self._l1d_prefetcher()))
        
        self.l1dcaches = l1dcaches

        # self.l1dcaches = [
        #     ThisL1DCache(prefetcher=self._prefetcher())
        #     for _ in range(board.get_processor().get_num_cores())
        # ]
        
        # Set up L2 Caches
        l2caches = []
        for _ in range(board.get_processor().get_num_cores()):
            if self._l2_prefetcher == None:
                l2caches.append(ThisL2Cache(prefetcher=self._general_prefetcher()))
            else:
                l2caches.append(ThisL2Cache(prefetcher=self._l2_prefetcher()))
        
        self.l2caches = l2caches
        
        self.l2buses = [
            L2XBar() for _ in range(board.get_processor().get_num_cores())
        ]

        # Set up L3 Cache
        if self._l3_prefetcher == None:
            self.l3cache = ThisL3Cache(prefetcher=self._general_prefetcher())
        else:
            self.l3cache = ThisL3Cache(prefetcher=self._l3_prefetcher())
        
        
        self.l3bus = L2XBar()

        # ITLB Page walk caches
        self.iptw_caches = [
            MMUCache(size="8kB") #forgot to check this with Mahyar but I believe this is correct
            for _ in range(board.get_processor().get_num_cores())
        ]
        # DTLB Page walk caches
        self.dptw_caches = [
            MMUCache(size="8kB") #same as line 122
            for _ in range(board.get_processor().get_num_cores())
        ]

        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):
            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            # Connect L1 caches to L2 buses
            self.l1icaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.l1dcaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.iptw_caches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.dptw_caches[i].mem_side = self.l2buses[i].cpu_side_ports

            # Connect L2 buses to L2 caches
            self.l2buses[i].mem_side_ports = self.l2caches[i].cpu_side

            # Connect L2 caches to L3 bus
            self.l2caches[i].mem_side = self.l3bus.cpu_side_ports

            cpu.connect_walker_ports(
                self.iptw_caches[i].cpu_side, self.dptw_caches[i].cpu_side
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()

        # Connect L3 bus to L3 cache
        self.l3bus.mem_side_ports = self.l3cache.cpu_side

        # Connect L3 cache to main memory bus
        self.membus.cpu_side_ports = self.l3cache.mem_side

    def _setup_io_cache(self, board: AbstractBoard) -> None: 
        """Create a cache for coherent I/O connections""" #Do not change
        self.iocache = Cache(
            assoc=8,
            tag_latency=50,
            data_latency=50,
            response_latency=50,
            mshrs=20,
            size="1kB",
            tgts_per_mshr=12,
            addr_ranges=board.mem_ranges,
        )
        self.iocache.mem_side = self.membus.cpu_side_ports
        self.iocache.cpu_side = board.get_mem_side_coherent_io_port()

# Specs are based off of the WikiChip for Skylake
# https://en.wikichip.org/wiki/intel/microarchitectures/skylake_(client)
class ThisL1DCache(L1DCache):
    def __init__(
        self,
        deg: int = 16,
        lat: int = 1,
        prefetcher: Prefetcher = StridePrefetcher(),
        ):
        super().__init__(
            size="32KiB",
            assoc=8,
            tag_latency=1,
            data_latency=1,
            response_latency=1,
            mshrs=128,
            tgts_per_mshr=16,
            writeback_clean=False,
            # prefetcher = StridePrefetcher(degree=16, latency=1)
        )
        if (hasattr(prefetcher, 'degree') and hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(degree=deg, latency=lat)
        elif (hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(latency=lat)
        else:
            self.prefetcher = prefetcher()


class ThisL1ICache(L1ICache):
    def __init__(
        self,
        deg: int = 2,
        lat: int = 1,
        prefetcher: Prefetcher = StridePrefetcher(),
        ):
        super().__init__(
            size="32KiB",
            assoc=8,
            tag_latency=1,
            data_latency=1,
            response_latency=1,
            mshrs=128,
            tgts_per_mshr=16,
            writeback_clean=False,
        )
        if (hasattr(prefetcher, 'degree') and hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(degree=deg, latency=lat)
        elif (hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(latency=lat)
        else:
            self.prefetcher = prefetcher()


class ThisL2Cache(L2Cache):
    def __init__(
        self,
        deg: int = 4,
        lat: int = 1,
        prefetcher: Prefetcher = StridePrefetcher(),
        ):
        super().__init__(
            size="256KiB",
            assoc=4,
            tag_latency=14,
            data_latency=14,
            response_latency=1,
            mshrs=256,
            tgts_per_mshr=16,
            writeback_clean=False,
        )
        if (hasattr(prefetcher, 'degree') and hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(degree=deg, latency=lat)
        elif (hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(latency=lat)
        else:
            self.prefetcher = prefetcher()


class ThisL3Cache(L2Cache):
    def __init__(
        self,
        deg: int = 2,
        lat: int = 1,
        prefetcher: Prefetcher = StridePrefetcher(),
        ):
        super().__init__(
            size="2MiB",
            assoc=16,
            tag_latency=44,
            data_latency=44,
            response_latency=1,
            mshrs=256,
            tgts_per_mshr=16,
            writeback_clean=False,
        )
        if (hasattr(prefetcher, 'degree') and hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(degree=deg, latency=lat)
        elif (hasattr(prefetcher, 'latency')):
            self.prefetcher = prefetcher(latency=lat)
        else:
            self.prefetcher = prefetcher()
