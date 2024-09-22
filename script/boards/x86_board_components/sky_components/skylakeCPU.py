#Authors: Jason Lowe-Power, Mitha Mysore, Alyssa Vallejo

from typing import Type

from .branch_pred import LTAGE_BP
from .skylake_core import SkyLakeStdCore

from m5.objects import (
    BranchPredictor,
)

from gem5.components.processors.base_cpu_processor import BaseCPUProcessor


# O3CPU along with BaseCPUProcessor wraps CPUCore to a processor
# compatible with gem5's standard library. Please refer to
#   gem5/src/python/gem5/components/processors/base_cpu_processor.py
# to learn more about BaseCPUProcessor.

class SkyLakeCPU(BaseCPUProcessor):
    def __init__(
        self,
        width: int = 4,
        depth: int = 3,
        num_cores: int = 1,
        branchPred: Type[BranchPredictor] = LTAGE_BP,
     ) -> None:
        """
        :param width: sets the width of fetch, decode, raname, issue, wb, and
        commit stages.
        """
        cores = [
            SkyLakeStdCore(width=width, depth=depth, branchPred=branchPred)
            for _ in range(num_cores)
        ]
        super().__init__(cores)
        self._width = width
        self._depth = depth
        self._branchPred = branchPred