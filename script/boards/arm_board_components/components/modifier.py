from abc import abstractmethod
from typing import final

from m5.objects.SimObject import SimObject

from gem5.components.boards.abstract_board import AbstractBoard
from gem5.utils.override import overrides


class Modifier:
    def __init__(self, description):
        self._desc = description

    def get_desc(self):
        return self._desc

    def __str__(self):
        return self._desc

    @abstractmethod
    def _get_simobjects(self, board: AbstractBoard):
        raise NotImplementedError

    @abstractmethod
    def _do_modification(self, sim_object: SimObject):
        raise NotImplementedError

    def apply(self, board: AbstractBoard):
        for sim_object in self._get_simobjects(board):
            self._do_modification(sim_object)


@final
class ModifierBundle(Modifier):
    _bundle_id = -1

    @classmethod
    def get_next_bundle_id(cls) -> int:
        cls._bundle_id += 1
        return cls._bundle_id

    def __init__(self, modifiers: list[Modifier]) -> None:
        id = ModifierBundle.get_next_bundle_id()
        description = f"Beginning of Modifier Bundle {id}:\n"
        description += "\n".join([mod.get_desc() for mod in modifiers])
        description += f"\nEnd of Modifier Bundle {id}."
        super().__init__(description)
        self._id = id
        self._modifiers = modifiers

    @overrides(Modifier)
    def _get_simobjects(self, board: AbstractBoard) -> list[SimObject]:
        pass

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject) -> None:
        pass

    @overrides(Modifier)
    def apply(self, board: AbstractBoard) -> None:
        for modifier in self._modifiers:
            modifier.apply(board)
