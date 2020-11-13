from scaife_viewer.atlas.hooks import DefaultHookSet
from scaife_viewer.atlas.resolvers.cts_collection import resolve_cts_collection_library
from scaife_viewer.core.cts import text_inventory


class ATLASHookSet(DefaultHookSet):
    def resolve_library(self):
        ti = text_inventory()
        return resolve_cts_collection_library(ti)
