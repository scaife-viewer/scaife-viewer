from MyCapytain.errors import UnknownCollection

from .capitains import default_resolver  # noqa
from .collections import (Collection, Text, TextGroup, TextInventory,  # noqa
                          Work, resolve_collection)
from .exceptions import CollectionDoesNotExist, PassageDoesNotExist
from .passage import Passage
from .reference import URN


def text_inventory() -> TextInventory:
    return TextInventory.load()


def collection(urn: str) -> Collection:
    try:
        metadata = TextInventory.load().metadata[urn]
    except UnknownCollection:
        raise CollectionDoesNotExist(f"{urn} does not exist")
    return resolve_collection(metadata.TYPE_URI)(URN(urn), metadata)


def passage(urn: str) -> Passage:
    urn = URN(urn)
    if urn.reference is None:
        raise ValueError("URN must contain a reference")
    reference = urn.reference
    urn = urn.upTo(URN.NO_PASSAGE)
    c = collection(urn)
    if isinstance(c, Work):
        work = c
        text = next((text for text in work.texts() if text.kind == "edition"), None)
        if text is None:
            raise ValueError(f"{urn} does not have an edition")
    elif isinstance(c, Text):
        text = c
    else:
        raise ValueError(f"{urn} must reference a work or text")
    passage = Passage(text, reference)
    if not passage.exists():
        raise PassageDoesNotExist(text, f"{reference} does not exist in {urn}")
    return passage
