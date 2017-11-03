from functools import lru_cache, partial

from MyCapytain.common.constants import RDF_NAMESPACES

from .capitains import resolver
from .passage import Passage
from .reference import URN
from .toc import RefTree
from .typing import CtsCollectionMetadata


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
            yield resolve_collection(metadata.TYPE_URI)(metadata.urn, metadata)


class TextGroup(Collection):

    def __repr__(self):
        return f"<cts.TextGroup {self.urn} at {hex(id(self))}>"

    def works(self):
        children = self.metadata.works
        for urn in sorted(children.keys()):
            yield Work(urn, children[urn])

    def as_json(self) -> dict:
        return {
            "urn": str(self.urn),
            "label": str(self.label),
            "works": [
                dict(urn=str(work.urn))
                for work in self.works()
            ],
        }


class Work(Collection):

    def __repr__(self):
        return f"<cts.Work {self.urn} at {hex(id(self))}>"

    def texts(self):
        children = self.metadata.texts
        for urn in sorted(children.keys()):
            metadata = children[urn]
            yield resolve_collection(metadata.TYPE_URI)(urn, metadata)

    def as_json(self) -> dict:
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
        depth = len(self.metadata.citation)
        tree = RefTree(self.urn, self.metadata.citation)
        for reff in resolver.getReffs(self.urn, level=depth):
            tree.add(reff)
        return tree

    def first_passage(self):
        chunk = next(self.toc().chunks(), None)
        if chunk is not None:
            return Passage(self, URN(chunk.urn).reference)

    def as_json(self) -> dict:
        toc = self.toc()
        return {
            "urn": str(self.urn),
            "label": str(self.label),
            "description": str(self.description),
            "kind": self.kind,
            "lang": self.lang,
            "human_lang": self.human_lang,
            "first_passage": dict(urn=str(self.first_passage().urn)),
            "toc": [
                {
                    "urn": next(toc.chunks(ref_node), None).urn,
                    "label": ref_node.label.title(),
                    "num": ref_node.num,
                }
                for ref_node in toc.num_resolver.glob(toc.root, "*")
            ],
        }


def resolve_collection(type_uri):
    return {
        RDF_NAMESPACES.CTS.term("textgroup"): TextGroup,
        RDF_NAMESPACES.CTS.term("work"): Work,
        RDF_NAMESPACES.CTS.term("edition"): partial(Text, "edition"),
        RDF_NAMESPACES.CTS.term("translation"): partial(Text, "translation"),
        RDF_NAMESPACES.CTS.term("commentary"): partial(Text, "commentary"),
    }[type_uri]
