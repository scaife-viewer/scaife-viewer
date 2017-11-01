from functools import lru_cache

from django.conf import settings

from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts import inventory as cts

from .capitains import retriever
from .collections import TextGroup


@lru_cache(maxsize=1)
def load_text_inventory_metadata() -> cts.CtsTextInventoryMetadata:
    if getattr(settings, "CTS_LOCAL_TEXT_INVENTORY", None) is not None:
        with open(settings.CTS_LOCAL_TEXT_INVENTORY, "r") as fp:
            ti_xml = fp.read()
    else:
        ti_xml = retriever.getCapabilities()
    return XmlCtsTextInventoryMetadata.parse(ti_xml)


class TextInventory:

    @classmethod
    def load(cls):
        return cls(load_text_inventory_metadata())

    def __init__(self, metadata: cts.CtsTextInventoryMetadata):
        self.metadata = metadata

    def __repr__(self):
        return f"<cts.TextInventory at {hex(id(self))}>"

    def text_groups(self):
        for urn in sorted(self.metadata.textgroups.keys()):
            yield TextGroup(urn, self.metadata.textgroups[urn])
