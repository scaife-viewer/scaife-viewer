from scaife_viewer.atlas.hooks import DefaultHookSet
from scaife_viewer.atlas.resolvers.cts_collection import resolve_cts_collection_library
from scaife_viewer.core.cts import text_inventory


class ATLASHookSet(DefaultHookSet):
    def resolve_library(self):
        ti = text_inventory()
        return resolve_cts_collection_library(ti)

    def extract_cts_text_group_metadata(self, text_group):
        metadata = super().extract_cts_text_group_metadata(text_group)
        # handle edge case where the group urn and version/work URNs differ
        # https://github.com/PersDigUMD/PDL/blob/1d9ec2450d62874f60dc5fd9e6c55c7048c5a36c/data/salman/__cts__.xml
        if metadata["urn"] == "urn:cts:perslit:sasalman:":
            metadata["urn"] = "urn:cts:perslit:salman:"
        return metadata

    # FIXME: handle other issues within PDL repo
