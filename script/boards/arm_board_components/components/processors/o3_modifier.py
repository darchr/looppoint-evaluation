from m5.objects.BaseO3CPU import BaseO3CPU
from m5.objects.SimpleTrace import SimpleTrace
from m5.proxy import Parent
from m5.util import inform

from gem5.components.boards.abstract_board import AbstractBoard
from gem5.utils.override import overrides

from ..modifier import Modifier


class O3Modifier(Modifier):
    def __init__(self, description):
        super().__init__(description)

    @overrides(Modifier)
    def _get_simobjects(self, board: AbstractBoard):
        cores = board.get_processor().get_cores()
        for core in cores:
            if not isinstance(core.get_simobject(), BaseO3CPU):
                raise ValueError(
                    f"This modifier ({self.__class__.__name__}) is "
                    "only applicable to O3CPU types."
                )

        return [core.get_simobject() for core in cores]


class BPModifier(O3Modifier):
    def __init__(self, bp_cls, **params):
        description = (
            f"Sets branch predictor to {bp_cls} "
            f"with the following parameters {params}."
        )
        super().__init__(description)
        self._bp_cls = bp_cls
        self._params = params.copy()
        if "numThreads" not in self._params:
            inform(
                "numThreads not passed in params. "
                "Setting it to the proxy Parent.numThreads."
            )
            self._params["numThreads"] = Parent.numThreads

    @overrides(Modifier)
    def _do_modification(self, sim_object):
        sim_object.branchPred = self._bp_cls(**self._params)


class SimpleTraceProbeModifier(O3Modifier):
    def __init__(self, **params):
        description = "Attaches a SimpleTrace proble to the CPU."
        super().__init__(description)
        self._params = params.copy()

    @overrides(Modifier)
    def _do_modification(self, sim_object):
        sim_object.simple_trace = SimpleTrace(**self._params)
