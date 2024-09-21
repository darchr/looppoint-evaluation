from abc import abstractmethod

from m5.objects import BaseISA, System

from gem5.isas import ISA
from gem5.utils.override import overrides

from .vector_processor import BaseVectorProcessor


class BaseVectorParameters:
    def __init__(self, is_fullsystem: bool):
        self.is_fullsystem = is_fullsystem

    def apply_system_change(self, system_object: System):
        self._apply_system_change(system_object)

    def apply_processor_change(self, processor: BaseVectorProcessor):
        for core in processor.get_core_simobjects():
            self._apply_isa_change(core.isa)
            self._apply_isa_change(core.decoder[0].isa)

    @abstractmethod
    def _apply_isa_change(self, isa_object: BaseISA):
        pass

    @abstractmethod
    def _apply_system_change(self, system_object: System):
        pass

    def isa(self):
        raise NotImplementedError


class ARM_SVE_Parameters(BaseVectorParameters):
    def __init__(self, vlen, is_fullsystem: bool):
        super().__init__(is_fullsystem)
        self.vlen = vlen
        # in gem5, the vector register length (vlen) is sve_vl * 128
        assert (vlen % 128 == 0) and (vlen > 0) and (vlen <= 2048)

    @overrides(BaseVectorParameters)
    def _apply_isa_change(self, isa_object: BaseISA):
        if not self.is_fullsystem:
            isa_object[0].sve_vl_se = self.vlen // 128

    @overrides(BaseVectorParameters)
    def _apply_system_change(self, system_object: System):
        if self.is_fullsystem:
            system_object.sve_vl = self.vlen // 128

    @overrides(BaseVectorParameters)
    def isa(self):
        return ISA.ARM


class RVV_Parameters(BaseVectorParameters):
    def __init__(self, elen, vlen, is_fullsystem: bool):
        super().__init__(is_fullsystem)
        self.elen = elen
        self.vlen = vlen

    @overrides(BaseVectorParameters)
    def _apply_isa_change(self, isa_object: BaseISA):
        isa_object[0].elen = self.elen
        isa_object[0].vlen = self.vlen

    @overrides(BaseVectorParameters)
    def _apply_system_change(self, system_object: System):
        raise NotImplementedError(
            "RVV configuration does not affect system object"
        )

    @overrides(BaseVectorParameters)
    def isa(self):
        return ISA.RISCV
