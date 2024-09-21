from .update_path import update_path

update_path()

from m5.objects.BranchPredictor import TAGE_SC_L_64KB

from components.processors.o3_modifier import BPModifier
from components.modifier import ModifierBundle


def get_bundle_from_version(version: int) -> ModifierBundle:
    return bundle_version[version]


bundle_version = {1: ModifierBundle([BPModifier(TAGE_SC_L_64KB)])}
