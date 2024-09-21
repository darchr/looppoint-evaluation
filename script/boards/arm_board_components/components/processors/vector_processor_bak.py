from typing import List, Union

from m5.util import warn

from gem5.isas import ISA
from gem5.utils.override import overrides
from gem5.components.boards.mem_mode import MemMode
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.processors.cpu_types import CPUTypes, get_mem_mode
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.switchable_processor import SwitchableProcessor

from .novo_core import NovoCore
from .vector_core import VectorCore
from .simple_vector_core import SimpleVectorCore


def _core_factory(isa: ISA, num_cores: int, core_type: Union[str, CPUTypes]):
    core_class = {
        "novo": NovoCore,
    }
    if isinstance(core_type, str):
        assert core_type in core_class
        return [core_class[core_type]() for _ in range(num_cores)]
    elif isinstance(core_type, CPUTypes):
        return [SimpleVectorCore(isa, core_type) for _ in range(num_cores)]
    else:
        raise ValueError(f"core_type can only be a string or CPUTypes.")


class BaseVectorProcessor(BaseCPUProcessor):
    def __init__(self, cores: List[VectorCore]):
        super().__init__(cores)

    def get_core_simobjects(self):
        return [core.get_core_simobject() for core in self.get_cores()]


class VectorProcessor(BaseVectorProcessor):
    def __init__(
        self, isa: ISA, num_cores: int, core_type: Union[str, CPUTypes]
    ):
        super().__init__(_core_factory(isa, num_cores, core_type))


class SwitchableVectorProcessor(SwitchableProcessor):
    def __init__(
        self,
        isa: ISA,
        num_cores: int,
        starting_core_type: Union[str, CPUTypes],
        switch_core_type: Union[str, CPUTypes],
    ) -> None:
        if num_cores <= 0:
            raise AssertionError("Number of cores must be a positive integer!")
        self._start_key = "warmup_cores"
        self._switch_key = "evaluation_cores"
        self._current_is_start = True
        self._mem_mode = get_mem_mode(starting_core_type)
        switchable_cores = {
            self._start_key: _core_factory(isa, num_cores, starting_core_type),
            self._switch_key: _core_factory(isa, num_cores, switch_core_type),
        }
        super().__init__(
            switchable_cores=switchable_cores, starting_cores=self._start_key
        )

    @overrides(SwitchableProcessor)
    def incorporate_processor(self, board: AbstractBoard) -> None:
        super().incorporate_processor(board=board)
        if (
            board.get_cache_hierarchy().is_ruby()
            and self._mem_mode == MemMode.ATOMIC
        ):
            warn(
                "Using an atomic core with Ruby will result in "
                "'atomic_noncaching' memory mode. This will skip caching "
                "completely."
            )
            self._mem_mode = MemMode.ATOMIC_NONCACHING
        board.set_mem_mode(self._mem_mode)

    def switch(self):
        """Switches to the "switched out" cores."""
        if self._current_is_start:
            self.switch_to_processor(self._switch_key)
        else:
            self.switch_to_processor(self._start_key)
        self._current_is_start = not self._current_is_start
