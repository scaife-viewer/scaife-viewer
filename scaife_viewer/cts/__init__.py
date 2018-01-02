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
    text = collection(urn)
    passage = Passage(text, reference)
    if not passage.exists():
        raise PassageDoesNotExist(text, f"{reference} does not exist in {urn}")
    return passage
