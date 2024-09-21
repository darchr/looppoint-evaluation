from m5.objects import BaseCPU

from gem5.isas import ISA
from gem5.components.processors.simple_core import BaseCPUCore


class VectorCore(BaseCPUCore):
    _next_version = -1

    @classmethod
    def version(cls):
        cls._next_version += 1
        return cls._next_version

    def __init__(self, isa: ISA, core: BaseCPU, type_name: str):
        core.cpu_id = VectorCore.version()
        super().__init__(core, isa)
        self._type_name = type_name

    def get_type_name(self):
        return self._type_name

    def get_core_simobject(self):
        return self.core

    def set_cpuid(self, cpu_id: int):
        self.core.cpu_id = cpu_id

    def get_cpuid(self):
        return self.core.cpu_id
