from .text_inventory import TextInventory
from .collections import (  # noqa
    Collection,
    TextGroup,
    Work,
    Text,
    resolve_collection,
)
from .passage import Passage
from .reference import URN


def text_inventory() -> TextInventory:
    return TextInventory.load()


def collection(urn: str) -> Collection:
    metadata = TextInventory.load().metadata[urn]
    return resolve_collection(metadata.TYPE_URI)(urn, metadata)


def passage(urn: str) -> Passage:
    urn = URN(urn)
    if urn.reference is None:
        raise ValueError("URN must contain a reference")
    reference = urn.reference
    urn = urn.upTo(URN.NO_PASSAGE)
    text = collection(urn)
    return Passage(text, reference)
