import os
import unicodedata
from collections import defaultdict
from functools import lru_cache

import anytree
import regex
from lxml import etree
from MyCapytain.common.constants import Mimetypes
from MyCapytain.common.reference import Reference

from .capitains import default_resolver
from .reference import URN


w = r"\w[-\w]*"
p = r"\p{P}+"
ws = r"[\p{Z}\s]+"
token_re = regex.compile(fr"{w}|{p}|{ws}")
w_re = regex.compile(w)
p_re = regex.compile(p)
ws_re = regex.compile(ws)


class Passage:

    def __init__(self, text, reference):
        self.text = text
        self.reference = reference
        if not isinstance(self.reference, Reference):
            self.reference = Reference(self.reference)

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
        return str(self.reference).split(".")[-1]

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
        text = self.textual_node().export(Mimetypes.PLAINTEXT)
        return unicodedata.normalize("NFC", text)

    def next(self):
        reference = self.textual_node().nextId
        if reference:
            return Passage(self.text, reference)

    def prev(self):
        reference = self.textual_node().prevId
        if reference:
            return Passage(self.text, reference)

    def tokenize(self, words=True, punctuation=True, whitespace=True):
        tokens = []
        idx = defaultdict(int)
        offset = 0
        for w in token_re.findall(self.content):
            if w:
                wl = len(w)
                if w_re.match(w):
                    offset += wl
                    if not words:
                        continue
                    t = "w"
                if p_re.match(w):
                    offset += wl
                    if not punctuation:
                        continue
                    t = "p"
                if ws_re.match(w):
                    if not whitespace:
                        continue
                    t = "s"
                for wk in (w[i:j + 1] for i in range(wl) for j in range(i, wl)):
                    idx[wk] += 1
                token = {
                    "w": w,
                    "i": idx[w],
                    "t": t,
                    "o": offset,
                }
                tokens.append(token)
        return tokens

    @lru_cache()
    def render(self):
        tei = self.textual_node().resource
        return TEIRenderer(tei)

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

    def as_json(self, with_content=True) -> dict:
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
                "lang": self.text.lang,
                "human_lang": self.text.human_lang,
                "kind": self.text.kind,
            },
            "refs": refs,
            "ancestors": [
                {
                    "reference": str(ancestor.reference),
                }
                for ancestor in self.ancestors()
            ],
            "children": [
                {
                    "reference": str(child.reference),
                    "lsb": child.lsb,
                }
                for child in self.children()
            ],
        }
        if with_content:
            o.update({
                "text_html": str(self.render()),
                "word_tokens": self.tokenize(punctuation=False, whitespace=False),
            })
        return o


class TEIRenderer:

    def __init__(self, tei):
        self.tei = tei
        self.indexes = defaultdict(int)
        self.offset = 0

    def __str__(self):
        return self.render()

    @lru_cache()
    def render(self):
        xsl_path = os.path.join(os.path.dirname(__file__), "tei.xsl")
        with open(xsl_path) as f:
            func_ns = "urn:python-funcs"
            transform = etree.XSLT(
                etree.XML(f.read()),
                extensions={
                    (func_ns, "tokens"): self.tokens,
                    (func_ns, "token_type"): self.token_type,
                    (func_ns, "token_index"): self.token_index,
                    (func_ns, "token_offset"): self.token_offset,
                }
            )
            try:
                return str(transform(self.tei))
            except Exception:
                for error in transform.error_log:
                    print(error.message, error.line)
                raise

    def tokens(self, context, value):
        ts = []
        v = "".join(value)
        for token in token_re.findall(v):
            if token:
                ts.append(unicodedata.normalize("NFC", token))
        return ts

    def token_type(self, context, value):
        v = "".join(value)
        if w_re.match(v):
            self.offset += len(v)
            return "w"
        if p_re.match(v):
            self.offset += len(v)
            return "p"
        if ws_re.match(v):
            return "s"

    def token_offset(self, context, value):
        v = "".join(value)
        return self.offset - len(v)

    def token_index(self, context, value):
        v = "".join(value)
        lv = len(v)
        for k in (v[i:j + 1] for i in range(lv) for j in range(i, lv)):
            self.indexes[k] += 1
        return self.indexes[v]
