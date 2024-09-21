from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.abstract_memory_system import AbstractMemorySystem
from gem5.components.processors.abstract_processor import AbstractProcessor
from gem5.components.cachehierarchies.abstract_cache_hierarchy import (
    AbstractCacheHierarchy,
)

from ..modifiable import MetaModifiable


class SyscallEmulationBoard(SimpleBoard, metaclass=MetaModifiable):
    def __init__(
        self,
        clk_freq: str,
        processor: AbstractProcessor,
        memory: AbstractMemorySystem,
        cache_hierarchy: AbstractCacheHierarchy,
    ):
        super().__init__(clk_freq, processor, memory, cache_hierarchy)
