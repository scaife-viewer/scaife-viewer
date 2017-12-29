from collections import defaultdict
from functools import lru_cache

import anytree
import regex
from lxml import etree
from MyCapytain.common.constants import Mimetypes

from .capitains import default_resolver
from .reference import URN


w = r"\w[-\w]*"
p = r"[\p{P}\p{C}]+"
ws = r"\p{Z}"
token_re = regex.compile(fr"{w}|{p}|{ws}")
w_re = regex.compile(w)
p_re = regex.compile(p)
ws_re = regex.compile(ws)


class Passage:

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference
        self.token_indexes = defaultdict(int)

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
            "start": self.text.toc().lookup(".".join(self.reference.start.list)),
        }
        if self.reference.end:
            ref_range["end"] = self.text.toc().lookup(".".join(self.reference.end.list))
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
            transform = etree.XSLT(
                etree.XML(f.read()),
                extensions={
                    ("urn:python-funcs", "tokens"): self.tokens,
                    ("urn:python-funcs", "token_type"): self.token_type,
                    ("urn:python-funcs", "token_index"): self.token_index,
                }
            )
            try:
                return transform(tei)
            except Exception:
                for error in transform.error_log:
                    print(error.message, error.line)
                raise

    def tokens(self, context, s):
        ts = []
        for token in token_re.findall("".join(s)):
            ts.append(token)
        return ts

    def token_type(self, context, value):
        v = "".join(value)
        if w_re.match(v):
            return "w"
        if p_re.match(v):
            return "p"
        if ws_re.match(v):
            return "s"

    def token_index(self, context, value):
        key = "".join(value)
        self.token_indexes[key] += 1
        return self.token_indexes[key]

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

    def as_json(self) -> dict:
        refs = {
            "start": {
                "reference": self.refs["start"].reference,
                "human_reference": self.refs["start"].human_reference,
            },
        }
        if "end" in self.refs:
            refs["end"] = {
                "reference": self.refs["end"].reference,
                "human_reference": self.refs["end"].human_reference,
            }
        o = {
            "urn": str(self.urn),
            "text": {
                "urn": str(self.text.urn),
                "label": self.text.label,
                "ancestors": [
                    {
                        "urn": str(ancestor.urn),
                        "label": ancestor.label,
                    }
                    for ancestor in self.text.ancestors()
                ],
                "human_lang": self.text.human_lang,
                "kind": self.text.kind,
            },
            "text_html": str(self.render()),
            "refs": refs,
            "ancestors": [
                {
                    "reference": ancestor.reference,
                }
                for ancestor in self.ancestors()
            ],
            "children": [
                {
                    "reference": child.reference,
                    "lsb": child.lsb,
                }
                for child in self.children()
            ],
        }
        return o
