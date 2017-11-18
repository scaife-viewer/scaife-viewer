from functools import lru_cache

import anytree
from lxml import etree
from MyCapytain.common.constants import Mimetypes

from .capitains import default_resolver
from .reference import URN


class Passage:

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference

    def __repr__(self):
        return f"<cts.Passage {self.urn} at {hex(id(self))}>"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.text.urn == other.text.urn and self.reference == other.reference
        return NotImplemented

    def __hash__(self):
        return hash(self.urn)

    def exists(self):
        try:
            # checks start and end for existence
            self.refs
        except anytree.ChildResolverError:
            return False
        return True

    @property
    def urn(self):
        return URN(f"{self.text.urn}:{self.reference}")

    @property
    def lsb(self):
        return self.reference.split(".")[-1]

    @lru_cache()
    def textual_node(self):
        # MyCapytain bug: local resolver getTextualNode can't take a Reference
        return default_resolver().getTextualNode(self.text.urn, subreference=str(self.reference))

    @property
    def refs(self):
        ref_range = {
            "start": self.text.toc().lookup(str(self.reference.start)),
        }
        if self.reference.end:
            ref_range["end"] = self.text.toc().lookup(str(self.reference.end))
        return ref_range

    @property
    def content(self):
        return self.textual_node().export(Mimetypes.PLAINTEXT)

    def next(self):
        reference = self.textual_node().nextId
        if reference:
            return Passage(self.text, reference)

    def prev(self):
        reference = self.textual_node().prevId
        if reference:
            return Passage(self.text, reference)

    @lru_cache()
    def render(self):
        tei = self.textual_node().resource
        with open("tei.xsl") as f:
            transform = etree.XSLT(etree.XML(f.read()))
            return transform(tei)

    def ancestors(self):
        toc = self.text.toc()
        toc_ref = toc.lookup(str(self.reference.start))
        for ancestor in toc_ref.ancestors[1:]:
            yield Passage(self.text, ancestor.reference)

    def children(self):
        toc = self.text.toc()
        toc_ref = toc.lookup(str(self.reference.start))
        for child in toc_ref.children:
            yield Passage(self.text, child.reference)
