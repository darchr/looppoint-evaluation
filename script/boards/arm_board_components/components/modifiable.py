from inspect import getmro

from m5.SimObject import MetaSimObject

from gem5.components.boards.abstract_board import AbstractBoard

from script.boards.arm_board_components.mods.update_path import update_path

update_path()

from .modifier import Modifier


class MetaModifiable(MetaSimObject):
    def __new__(cls, name, bases, dct):
        def _find_board_base(bases):
            for base in bases:
                if issubclass(base, AbstractBoard):
                    return base
            return None

        def _find_pre_instantiate(base):
            for candidate in getmro(base):
                if "_pre_instantiate" in candidate.__dict__:
                    break
            return candidate._pre_instantiate

        def add_modifier(self, modifier: Modifier):
            self._modifiers.append(modifier)

        def _apply_modifiers(self):
            for modifier in self._modifiers:
                modifier.apply(self)

        dct["_modifiers"] = []
        dct["add_modifier"] = add_modifier
        dct["_apply_modifiers"] = _apply_modifiers

        original_pre_instantiate = dct.get("_pre_instantiate")
        if original_pre_instantiate is None:
            board_base = _find_board_base(bases)
            if board_base is None:
                raise TypeError(
                    "MetaModifiable must be used with an AbstractBoard base."
                )
            original_pre_instantiate = _find_pre_instantiate(board_base)
        assert original_pre_instantiate is not None

        def new_pre_instantiate(self):
            original_pre_instantiate(self)
            self._apply_modifiers()

        dct["_pre_instantiate"] = new_pre_instantiate

        return super().__new__(cls, name, bases, dct)
