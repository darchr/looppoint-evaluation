from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_core import SimpleCore

from .vector_core import VectorCore


class SimpleVectorCore(VectorCore):
    def __init__(self, isa: ISA, cpu_type: CPUTypes):
        super().__init__(
            isa,
            SimpleCore.cpu_simobject_factory(cpu_type, isa, -1),
            f"Simple{cpu_type}",
        )
