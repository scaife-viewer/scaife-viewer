from typing import NamedTuple

from lxml import etree
from MyCapytain.common.constants import XPATH_NAMESPACES
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import xmlparser
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.texts.remote.cts import CtsText
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


class Resource(NamedTuple):

    urn: str
    label: str
    readable: bool


class CTS:
    """
    Thin-wrapper around calling into MyCapytian library. This class provides
    domain-specific implementations.
    """

    def is_resource(self, urn):
        urn = URN(urn)
        if urn.upTo(URN.TEXTGROUP) == str(urn):
            return True
        if urn.upTo(URN.WORK) == str(urn):
            return True
        if urn.upTo(URN.VERSION) == str(urn):
            return True
        return False

    def resources(self, urn=None):
        if urn:
            urn = URN(urn)
        # The follow code is a super simple way of traversing a CTS API.
        # This is effectively the same as resolver.getMetadata, but tweaked very slightly
        # to allow displaying a the collection of text groups.
        retriever = HttpCtsRetriever("https://perseus-cts.us1.eldarioncloud.com/api/cts")
        ti = XmlCtsTextInventoryMetadata.parse(retriever.getCapabilities(urn=urn))
        if urn:
            ti = [x for x in [ti] + ti.descendants if x.id == str(urn)][0]
        resources = []
        for o in ti.members:
            resource = Resource(
                urn=o.id,
                label=o.get_label(lang="eng"),
                readable=o.readable,
            )
            resources.append(resource)
        return resources

    def first_urn(self, urn):
        retriever = HttpCtsRetriever("https://perseus-cts.us1.eldarioncloud.com/api/cts")
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

    @classmethod
    def load(cls, urn):
        urn = URN(urn)
        retriever = HttpCtsRetriever("https://perseus-cts.us1.eldarioncloud.com/api/cts")
        resolver = HttpCtsResolver(retriever)
        node = resolver.getTextualNode(urn)
        return cls(urn, node)

    def __init__(self, urn, node):
        self.urn = urn
        self.node = node

    def next_urn(self):
        return f"{self.urn.upTo(URN.NO_PASSAGE)}:{self.node.nextId}" if self.node.nextId else None

    def prev_urn(self):
        return f"{self.urn.upTo(URN.NO_PASSAGE)}:{self.node.prevId}" if self.node.prevId else None

    def ancestors(self):
        ancs = []
        ref = self.urn.reference
        parent = ref.parent
        while parent is not None:
            ancs.append({
                "urn": f"{self.urn.upTo(URN.NO_PASSAGE)}:{parent}",
                "label": str(parent),
            })
            parent = parent.parent
        return ancs

    def render(self):
        tei = self.node.resource
        with open("tei.xsl") as f:
            transform = etree.XSLT(etree.XML(f.read()))
        return transform(tei)
