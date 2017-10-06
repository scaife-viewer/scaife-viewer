import collections
import operator

from typing import Any, NamedTuple

from django.conf import settings

from lxml import etree
from MyCapytain.common.constants import XPATH_NAMESPACES, RDF_NAMESPACES
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import xmlparser
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


attrgetter = operator.attrgetter


class Resource(NamedTuple):

    urn: str
    label: str
    readable: bool


class Textgroup(NamedTuple):

    resource: Any
    kind: str = "textgroup"

    def works(self):
        return [
            Work(resource=work)
            for work in sorted(self.resource.works.values(), key=attrgetter("id"))
        ]


class Work(NamedTuple):

    resource: Any
    kind: str = "work"

    def texts(self):
        texts_sorted = sorted(self.resource.texts.values(), key=attrgetter("id"))
        r = []
        for text in texts_sorted:
            if text.TYPE_URI == RDF_NAMESPACES.CTS.term("edition"):
                r.append(Text(resource=text, subkind="edition"))
            if text.TYPE_URI == RDF_NAMESPACES.CTS.term("translation"):
                r.append(Text(resource=text, subkind="translation"))
            if text.TYPE_URI == RDF_NAMESPACES.CTS.term("commentary"):
                r.append(Text(resource=text, subkind="commentary"))
        return r


class Text(NamedTuple):

    resource: Any
    subkind: str
    kind: str = "text"

    @property
    def human_lang(self):
        lang = self.resource.lang
        return {
            "grc": "Greek",
            "lat": "Latin",
            "heb": "Hebrew",
            "fa":  "Farsi",
            "eng": "English",
            "ger": "German",
            "fre": "French",
        }.get(lang, lang)


class CTS:
    """
    Thin-wrapper around calling into MyCapytain library. This class provides
    domain-specific implementations.
    """

    cache = {}

    def is_resource(self, urn):
        urn = URN(urn)
        if urn.upTo(URN.TEXTGROUP) == str(urn):
            return True
        if urn.upTo(URN.WORK) == str(urn):
            return True
        if urn.upTo(URN.VERSION) == str(urn):
            return True
        return False

    def resource(self, urn):
        urn = URN(urn)
        retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        resolver = HttpCtsResolver(retriever)
        r = resolver.getMetadata(str(urn))
        if r.TYPE_URI == RDF_NAMESPACES.CTS.term("textgroup"):
            return Textgroup(resource=r)
        if r.TYPE_URI == RDF_NAMESPACES.CTS.term("work"):
            return Work(resource=r)
        if r.TYPE_URI == RDF_NAMESPACES.CTS.term("edition"):
            return Text(resource=r, subkind="edition")
        if r.TYPE_URI == RDF_NAMESPACES.CTS.term("translation"):
            return Text(resource=r, subkind="translation")
        if r.TYPE_URI == RDF_NAMESPACES.CTS.term("commentary"):
            return Text(resource=r, subkind="commentary")
        raise Exception(f"not supported: {r.TYPE_URI}")

    def resources(self, urn=None):
        key = urn
        if key in self.cache:
            return self.cache[key]
        else:
            if urn:
                urn = URN(urn)
            # The follow code is a super simple way of traversing a CTS API.
            # This is effectively the same as resolver.getMetadata, but tweaked very slightly
            # to allow displaying a the collection of text groups.
            retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
            ti = XmlCtsTextInventoryMetadata.parse(retriever.getCapabilities(urn=urn))
            if urn:
                ti = [x for x in [ti] + ti.descendants if x.id == str(urn)][0]
            resources = []
            members = sorted(ti.members, key=operator.attrgetter("id"))
            for o in members:
                resource = Resource(
                    urn=o.id,
                    label=o.get_label(lang="eng"),
                    readable=o.readable,
                )
                resources.append(resource)
            self.cache[key] = resources
            return resources

    def toc(self, urn, level=None, group_size=20):
        retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        resolver = HttpCtsResolver(retriever)
        text = self.resource(urn)
        c_len = len(text.resource.citation)
        if level is None or level > c_len:
            level = c_len
        references = resolver.getReffs(urn, level=level)
        _refs = collections.OrderedDict()
        _refs2 = collections.OrderedDict()
        for ref in references:
            key = (text.resource.citation.name, ".".join(ref.split(".")[:level - 1]))
            _refs.setdefault(key, []).append(ref)
        for key, refs in _refs.items():
            grouped = [
                refs[i:i + group_size]
                for i in range(0, len(refs), group_size)
            ]
            _refs2[key] = [
                join_or_single(ref[0], ref[-1])
                for ref in grouped
            ]
        return _refs2

    def first_urn(self, urn):
        retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        resource = xmlparser(retriever.getFirstUrn(urn))
        first_urn = resource.xpath(
            "//ti:reply/ti:first/ti:urn/text()",
            namespaces=XPATH_NAMESPACES,
            magic_string=True,
        )
        if first_urn:
            return str(first_urn[0])

    def passage(self, urn):
        return Passage.load(urn)


class Passage:

    cache = {}

    @classmethod
    def load(cls, urn):
        urn = URN(urn)
        retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        resolver = HttpCtsResolver(retriever)
        metadata = resolver.getMetadata(urn.upTo(URN.NO_PASSAGE))
        textual_node = resolver.getTextualNode(urn)
        return cls(urn, metadata, textual_node)

    def __init__(self, urn, metadata, textual_node):
        self.urn = urn
        self.metadata = metadata
        self.textual_node = textual_node

    @property
    def lang(self):
        return self.metadata.lang

    @property
    def rtl(self):
        return self.lang in {"heb"}

    def next_urn(self):
        return f"{self.urn.upTo(URN.NO_PASSAGE)}:{self.textual_node.nextId}" if self.textual_node.nextId else None

    def prev_urn(self):
        return f"{self.urn.upTo(URN.NO_PASSAGE)}:{self.textual_node.prevId}" if self.textual_node.prevId else None

    def ancestors(self):
        key = f"ancestor-{self.urn}"
        if key not in self.cache:
            ancestors = []
            ref = self.urn.reference
            parent = ref.parent
            while parent is not None:
                ancestors.append({
                    "urn": f"{self.urn.upTo(URN.NO_PASSAGE)}:{parent}",
                    "label": str(parent),
                })
                parent = parent.parent
            self.cache[key] = ancestors
        return self.cache[key]

    def render(self):
        key = f"render-{self.urn}"
        if key not in self.cache:
            tei = self.textual_node.resource
            with open("tei.xsl") as f:
                transform = etree.XSLT(etree.XML(f.read()))
            self.cache[key] = transform(tei)
        return self.cache[key]


def join_or_single(start, end):
    return start if start == end else f"{start}-{end}"
