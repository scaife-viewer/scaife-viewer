from functools import lru_cache, partial
from operator import attrgetter

from django.conf import settings

from MyCapytain.common.constants import RDF_NAMESPACES
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts import inventory as cts

from .capitains import default_resolver
from .passage import Passage
from .reference import URN
from .toc import RefTree
from .typing import CtsCollectionMetadata


@lru_cache(maxsize=1)
def load_text_inventory_metadata() -> cts.CtsTextInventoryMetadata:
    resolver_type = settings.CTS_RESOLVER["type"]
    resolver = default_resolver()
    if resolver_type == "api":
        if getattr(settings, "CTS_LOCAL_TEXT_INVENTORY", None) is not None:
            with open(settings.CTS_LOCAL_TEXT_INVENTORY, "r") as fp:
                ti_xml = fp.read()
        else:
            ti_xml = resolver.endpoint.getCapabilities()
        return XmlCtsTextInventoryMetadata.parse(ti_xml)
    elif resolver_type == "local":
        return resolver.getMetadata()["default"]


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
            text_group = TextGroup(urn, self.metadata.textgroups[urn])
            if next(text_group.works(), None) is None:
                continue
            yield text_group


class Collection:

    def __init__(self, urn: URN, metadata: CtsCollectionMetadata):
        self.urn = urn
        self.metadata = metadata

    def __repr__(self):
        return f"<cts.Collection {self.urn} at {hex(id(self))}>"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.urn == other.urn
        return NotImplemented

    def __hash__(self):
        return hash(str(self.urn))

    @property
    def label(self):
        return self.metadata.get_label(lang="eng")

    def ancestors(self):
        for metadata in list(reversed(self.metadata.parents))[1:]:
            cls = resolve_collection(metadata.TYPE_URI)
            # the local resolver returns the text inventory from parents
            # this is isn't a proper ancestor here so we'll ignore it.
            if issubclass(cls, TextInventory):
                continue
            yield cls(metadata.urn, metadata)


class TextGroup(Collection):

    def __repr__(self):
        return f"<cts.TextGroup {self.urn} at {hex(id(self))}>"

    def works(self):
        children = self.metadata.works
        for urn in sorted(children.keys()):
            work = Work(urn, children[urn])
            if next(work.texts(), None) is None:
                continue
            yield work

    def as_json(self, **kwargs) -> dict:
        return {
            "urn": str(self.urn),
            "label": str(self.label),
            "works": [
                {
                    "urn": str(work.urn),
                    "texts": [
                        {
                            "urn": str(text.urn),
                        }
                        for text in work.texts()
                    ],
                }
                for work in self.works()
            ],
        }


class Work(Collection):

    def __repr__(self):
        return f"<cts.Work {self.urn} at {hex(id(self))}>"

    def texts(self):
        children = self.metadata.texts
        texts = []
        for urn in children.keys():
            metadata = children[urn]
            if metadata.citation is None:
                continue
            texts.append(resolve_collection(metadata.TYPE_URI)(urn, metadata))
        yield from sorted(texts, key=attrgetter("kind", "label"))

    def as_json(self, **kwargs) -> dict:
        return {
            "urn": str(self.urn),
            "label": str(self.label),
            "texts": [
                dict(urn=str(text.urn))
                for text in self.texts()
            ],
        }


class Text(Collection):

    def __init__(self, kind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind

    def __repr__(self):
        return f"<cts.Text {self.urn} kind={self.kind} at {hex(id(self))}>"

    @property
    def description(self):
        return self.metadata.get_description(lang="eng")

    @property
    def lang(self):
        return self.metadata.lang

    @property
    def human_lang(self):
        lang = self.metadata.lang
        return {
            "grc": "Greek",
            "lat": "Latin",
            "heb": "Hebrew",
            "fa": "Farsi",
            "eng": "English",
            "ger": "German",
            "fre": "French",
        }.get(lang, lang)

    @property
    def rtl(self):
        return self.lang in {"heb", "fa"}

    def versions(self):
        for edition in self.metadata.editions():
            yield Text("edition", edition.urn, edition)
        for translation in self.metadata.translations():
            yield Text("translation", translation.urn, translation)

    @lru_cache()
    def toc(self):
        citation = self.metadata.citation
        depth = len(citation)
        tree = RefTree(self.urn, citation)
        try:
            reffs = default_resolver().getReffs(self.urn, level=depth)
            for reff in reffs:
                tree.add(reff)
            return tree
        except Exception:
            raise ValueError(f"{self.urn} has an invalid refsDecl")

    def first_passage(self):
        chunk = next(self.toc().chunks(), None)
        if chunk is not None:
            return Passage(self, URN(chunk.urn).reference)

    def as_json(self, **kwargs) -> dict:
        with_toc = kwargs.pop("with_toc", False)
        payload = {
            "urn": str(self.urn),
            "label": str(self.label),
            "description": str(self.description),
            "kind": self.kind,
            "lang": self.lang,
            "rtl": self.rtl,
            "human_lang": self.human_lang,
        }
        if with_toc:
            toc = self.toc()
            payload.update({
                "first_passage": dict(urn=str(self.first_passage().urn)),
                "ancestors": [
                    {
                        "urn": str(ancestor.urn),
                        "label": ancestor.label,
                    }
                    for ancestor in self.ancestors()
                ],
                "toc": [
                    {
                        "urn": next(toc.chunks(ref_node), None).urn,
                        "label": ref_node.label.title(),
                        "num": ref_node.num,
                    }
                    for ref_node in toc.num_resolver.glob(toc.root, "*")
                ],
            })
        return payload


def resolve_collection(type_uri):
    return {
        RDF_NAMESPACES.CTS.term("TextInventory"): TextInventory,
        RDF_NAMESPACES.CTS.term("textgroup"): TextGroup,
        RDF_NAMESPACES.CTS.term("work"): Work,
        RDF_NAMESPACES.CTS.term("edition"): partial(Text, "edition"),
        RDF_NAMESPACES.CTS.term("translation"): partial(Text, "translation"),
        RDF_NAMESPACES.CTS.term("commentary"): partial(Text, "commentary"),
    }[type_uri]
