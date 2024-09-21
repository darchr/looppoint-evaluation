from gem5.components.boards.test_board import TestBoard
from gem5.components.memory.abstract_memory_system import AbstractMemorySystem
from gem5.components.processors.abstract_generator import AbstractGenerator
from gem5.components.cachehierarchies.abstract_cache_hierarchy import (
    AbstractCacheHierarchy,
)

from ..modifiable import MetaModifiable


class SynthTrafficBoard(TestBoard, metaclass=MetaModifiable):
    def __init__(
        self,
        clk_freq: str,
        generator: AbstractGenerator,
        cache_hierarchy: AbstractCacheHierarchy,
        memory: AbstractMemorySystem,
    ):
        super().__init__(clk_freq, generator, memory, cache_hierarchy)
