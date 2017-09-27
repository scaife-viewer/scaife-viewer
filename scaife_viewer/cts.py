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
        return sorted(self.resource.works.values(), key=attrgetter("id"))


class Work(NamedTuple):

    resource: Any
    kind: str = "work"

    def texts(self):
        return sorted(self.resource.texts.values(), key=attrgetter("id"))


class CTS:
    """
    Thin-wrapper around calling into MyCapytian library. This class provides
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
