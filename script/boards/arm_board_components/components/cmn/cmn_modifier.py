from typing import Type

from m5.objects.Prefetcher import BasePrefetcher
from m5.objects.SimObject import SimObject
from m5.params import NullSimObject
from m5.util import inform

from gem5.components.boards.abstract_board import AbstractBoard
from gem5.utils.override import overrides

from ..modifier import Modifier
from script.boards.arm_board_components.components.cmn import CoherentMeshNetwork
# from .cmn import CoherentMeshNetwork


class CMNModifier(Modifier):
    def __init__(self, description):
        super().__init__(description)

    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        raise NotImplementedError

    @overrides(Modifier)
    def _get_simobjects(self, board: AbstractBoard):
        cache_hierarchy = board.get_cache_hierarchy()
        if not isinstance(cache_hierarchy, CoherentMeshNetwork):
            raise ValueError(
                f"This modifier ({self.__class__.__name__}) is "
                "only applicable to CoherentMeshNetwork."
            )
        return self._get_simobjects_from_cache_hierarchy(cache_hierarchy)


class CMNPrefetcherModifier(CMNModifier):
    def __init__(
        self,
        description,
        prefetcher_cls: Type[BasePrefetcher],
        **params,
    ):
        super().__init__(description)
        self._prefetcher_cls = prefetcher_cls
        self._params = params.copy()

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.prefetcher = self._prefetcher_cls(**self._params)
        sim_object.use_prefetcher = not isinstance(
            sim_object.prefetcher, NullSimObject
        )


class CMNL1DPrefetcherModifier(CMNPrefetcherModifier):
    def __init__(
        self,
        prefetcher_cls: Type[BasePrefetcher],
        **params,
    ):
        super().__init__(
            f"Sets dcache prefetcher to {prefetcher_cls} "
            f"with the following parameters {params}",
            prefetcher_cls,
            **params,
        )

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            cluster.dcache
            for core_tile in cache_hierarchy.core_tiles
            for cluster in core_tile.core_clusters
        ]


class CMNL1IPrefetcherModifier(CMNPrefetcherModifier):
    def __init__(
        self,
        prefetcher_cls: Type[BasePrefetcher],
        **params,
    ):
        super().__init__(
            f"Sets icache prefetcher to {prefetcher_cls} "
            f"with the following parameters {params}",
            prefetcher_cls,
            **params,
        )

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            cluster.icache
            for core_tile in cache_hierarchy.core_tiles
            for cluster in core_tile.core_clusters
        ]


class CMNL2PrefetcherModifier(CMNPrefetcherModifier):
    def __init__(
        self,
        prefetcher_cls: Type[BasePrefetcher],
        **params,
    ):
        super().__init__(
            f"Sets l2cache prefetcher to {prefetcher_cls} "
            f"with the following parameters {params}",
            prefetcher_cls,
            **params,
        )

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            cluster.l2cache
            for core_tile in cache_hierarchy.core_tiles
            for cluster in core_tile.core_clusters
        ]


class CMNClusterLatModifier(CMNModifier):
    def __init__(self, ext_latency: int, int_latency: int):
        description = (
            f"Sets ext_routing_latency for cluster routers to {ext_latency} "
            f"and int_routing_latency for cluster routers to {int_latency}."
        )
        if not (ext_latency > 0 and int_latency > 0):
            raise ValueError(
                "ext_latency and int_latency should be greater than 0."
            )
        super().__init__(description)
        self._ext_latency = ext_latency
        self._int_latency = int_latency

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            cluster.router
            for core_tile in cache_hierarchy.core_tiles
            for cluster in core_tile.core_clusters
        ]

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.ext_routing_latency = self._ext_latency
        sim_object.int_routing_latency = self._int_latency


class CMNSystemLatModifier(CMNModifier):
    def __init__(self, ext_latency: int, int_latency: int):
        description = (
            f"Sets ext_routing_latency for system routers to {ext_latency} "
            f"and int_routing_latency for system routers to {int_latency}."
        )
        if not (ext_latency > 0 and int_latency > 0):
            raise ValueError(
                "ext_latency and int_latency should be greater than 0."
            )
        super().__init__(description)
        self._ext_latency = ext_latency
        self._int_latency = int_latency

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            router
            for router in cache_hierarchy.ruby_system.network.system_routers
        ]

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.ext_routing_latency = self._ext_latency
        sim_object.int_routing_latency = self._int_latency


class CMNMemoryLatModifier(CMNModifier):
    def __init__(self, ext_latency: int, int_latency: int):
        description = (
            f"Sets ext_routing_latency for memory routers to {ext_latency} "
            f"and int_routing_latency for memory routers to {int_latency}."
        )
        if not (ext_latency > 0 and int_latency > 0):
            raise ValueError(
                "ext_latency and int_latency should be greater than 0."
            )
        super().__init__(description)
        self._ext_latency = ext_latency
        self._int_latency = int_latency

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return [
            router
            for router in cache_hierarchy.ruby_system.network.memory_routers
        ]

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.ext_routing_latency = self._ext_latency
        sim_object.int_routing_latency = self._int_latency


class CMNDMALatModifier(CMNModifier):
    def __init__(self, ext_latency: int, int_latency: int):
        description = (
            f"Sets ext_routing_latency for DMA routers to {ext_latency} "
            f"and int_routing_latency for DMA routers to {int_latency}."
        )
        if not (ext_latency > 0 and int_latency > 0):
            raise ValueError(
                "ext_latency and int_latency should be greater than 0."
            )
        super().__init__(description)
        self._ext_latency = ext_latency
        self._int_latency = int_latency

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        if not hasattr(cache_hierarchy.ruby_system.network, "dma_routers"):
            inform(
                f"{self.__class__.__name__} did not find any DMA routers. "
                "Skipping the modification."
            )
            return []
        return [
            router
            for router in cache_hierarchy.ruby_system.network.dma_routers
        ]

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.ext_routing_latency = self._ext_latency
        sim_object.int_routing_latency = self._int_latency


class CMNReplPolModifier(CMNModifier):
    def __init__(self, repl_policy_cls, **params):
        description = (
            f"Sets replacement policy to {repl_policy_cls} "
            f"with the following parameters {params}."
        )
        super().__init__(description)
        self._repl_policy_cls = repl_policy_cls
        self._params = params.copy()

    @overrides(CMNModifier)
    def _get_simobjects_from_cache_hierarchy(self, cache_hierarchy):
        return (
            [
                cluster.dcache.cache
                for core_tile in cache_hierarchy.core_tiles
                for cluster in core_tile.core_clusters
            ]
            + [
                cluster.icache.cache
                for core_tile in cache_hierarchy.core_tiles
                for cluster in core_tile.core_clusters
            ]
            + [
                cluster.l2cache.cache
                for core_tile in cache_hierarchy.core_tiles
                for cluster in core_tile.core_clusters
            ]
        )

    @overrides(Modifier)
    def _do_modification(self, sim_object: SimObject):
        sim_object.replacement_policy = self._repl_policy_cls(**self._params)
