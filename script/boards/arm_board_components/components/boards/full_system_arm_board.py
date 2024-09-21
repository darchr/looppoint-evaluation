from m5.util import inform

from m5.objects.ArmSystem import ArmDefaultRelease
from m5.objects.RealView import VExpress_GEM5_V1, VExpress_GEM5_Foundation

from gem5.utils.override import overrides
from gem5.components.boards.arm_board import ArmBoard

from ..modifiable import MetaModifiable


class FullSystemArmBoard(ArmBoard, metaclass=MetaModifiable):
    def __init__(
        self,
        clk_freq: str,
        processor,
        cache_hierarchy,
        memory,
        use_kvm: bool = False,
    ):
        release = (
            ArmDefaultRelease().for_kvm() if use_kvm else ArmDefaultRelease()
        )
        platform = (
            VExpress_GEM5_V1() if use_kvm else VExpress_GEM5_Foundation()
        )
        super().__init__(
            clk_freq, processor, memory, cache_hierarchy, platform, release
        )
        self._use_systemd = True
        self._init_path = None

    def set_init_path(self, path: str):
        if not self._use_systemd:
            assert self._init_path is None
            raise RuntimeError("Already called set_init_path once.")
        self._use_systemd = False
        self._init_path = path

    @overrides(ArmBoard)
    def get_default_kernel_args(self):
        tail = [f"init={self._init_path}"] if not self._use_systemd else []
        return [
            "console=ttyAMA0",
            "lpj=19988480",
            "norandmaps",
            "root=/dev/vda1",
            "rw",
            f"mem={self.get_memory().get_size()}",
        ] + tail

    @overrides(ArmBoard)
    def _pre_instantiate(self):
        super()._pre_instantiate()
        if self._use_systemd:
            inform(
                f"By default this board boots up with systemd. "
                "If you wish to boot with a specific init script, "
                "please use set_init_path to point the board to the "
                "location (on your disk) where your init script is located."
            )
