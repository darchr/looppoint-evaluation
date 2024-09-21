from m5.objects import (
    BadAddr,
    BaseXBar,
    Cache,
    L2XBar,
    Port,
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
        membus = SystemXBar(width=64)
        membus.badaddr_responder = BadAddr()
        membus.default = membus.badaddr_responder.pio
        return membus

    def __init__(
        self,
        l1d_size: str = "64KiB",
        l1d_assoc: int = 4,
        l1i_size: str = "64KiB",
        l1i_assoc: int = 4,
        l2_size: str = "1MiB",
        l2_assoc: int = 8,
        l3_size: str = "32MiB",
        l3_assoc: int = 16,
        membus: BaseXBar = _get_default_membus.__func__(),
    ) -> None:

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

        # self.l1icaches = [
        #     L1ICache(
        #         size=self._l1i_size,
        #         assoc=self._l1i_assoc,
        #     )
        #     for _ in range(board.get_processor().get_num_cores())
        # ]
        self.l1icaches = [
            ThisL1ICache()
            for _ in range(board.get_processor().get_num_cores())
        ]

        # self.l1dcaches = [
        #     L1DCache(
        #         size=self._l1d_size,
        #         assoc=self._l1d_assoc,
        #     )
        #     for _ in range(board.get_processor().get_num_cores())
        # ]
        self.l1dcaches = [
            ThisL1DCache()
            for _ in range(board.get_processor().get_num_cores())
        ]

        # self.l2caches = [
        #     L2Cache(
        #         size=self._l2_size,
        #         assoc=self._l2_assoc,
        #     )
        #     for _ in range(board.get_processor().get_num_cores())
        # ]
        self.l2caches = [
            ThisL2Cache() for _ in range(board.get_processor().get_num_cores())
        ]
        self.l2buses = [
            L2XBar() for _ in range(board.get_processor().get_num_cores())
        ]

        # self.l3cache = L2Cache(
        #     size=self._l3_size,
        #     assoc=self._l3_assoc,
        # )
        self.l3cache = ThisL3Cache()
        self.l3bus = L2XBar()

        # ITLB Page walk caches
        self.iptw_caches = [
            MMUCache(size="8KiB")
            for _ in range(board.get_processor().get_num_cores())
        ]
        # DTLB Page walk caches
        self.dptw_caches = [
            MMUCache(size="8KiB")
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
        """Create a cache for coherent I/O connections"""
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


class ThisL1DCache(L1DCache):
    def __init__(self):
        super().__init__(
            size="64KiB",
            assoc=4,
            tag_latency=1,
            data_latency=1,
            response_latency=1,
            mshrs=16,
            tgts_per_mshr=20,
            writeback_clean=False,
        )
        self.prefetcher = StridePrefetcher(degree=16, latency=1)


class ThisL1ICache(L1ICache):
    def __init__(self):
        super().__init__(
            size="64KiB",
            assoc=4,
            tag_latency=1,
            data_latency=1,
            response_latency=1,
            mshrs=16,
            tgts_per_mshr=20,
            writeback_clean=False,
        )
        self.prefetcher = StridePrefetcher(degree=2, latency=1)


class ThisL2Cache(L2Cache):
    def __init__(self):
        super().__init__(
            size="1MiB",
            assoc=8,
            tag_latency=10,
            data_latency=10,
            response_latency=1,
            mshrs=20,
            tgts_per_mshr=8,
            writeback_clean=False,
        )
        self.prefetcher = StridePrefetcher(degree=4, latency=1)


class ThisL3Cache(L2Cache):
    def __init__(self):
        super().__init__(
            size="32MiB",
            assoc=16,
            tag_latency=20,
            data_latency=20,
            response_latency=1,
            mshrs=20,
            tgts_per_mshr=8,
            writeback_clean=False,
        )
        self.prefetcher = NULL
