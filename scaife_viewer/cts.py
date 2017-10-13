import itertools
import re
from itertools import zip_longest
from operator import attrgetter, methodcaller, itemgetter
from typing import Any, NamedTuple

from django.conf import settings

import anytree
import anytree.iterators
from lxml import etree
from MyCapytain.common.constants import RDF_NAMESPACES
from MyCapytain.common.reference import URN
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


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
            "fa": "Farsi",
            "eng": "English",
            "ger": "German",
            "fre": "French",
        }.get(lang, lang)


class RefTreeDepthIter(anytree.iterators.PreOrderIter):

    def __init__(self, node, depth=0):
        super(RefTreeDepthIter, self).__init__(node, filter_=self.filter_func(depth + 1))

    def filter_func(self, depth):
        def f(node):
            return node.depth == depth
        return f


class RefTree:

    def __init__(self, urn, citations):
        self.urn = urn
        self.citations = citations
        self.root = RefNode()
        self.ancestor_cache = {}
        self.num_resolver = anytree.Resolver("num")

    def add(self, reff):
        # zip together the citation labels with the reff:
        #   citations = ["book", "line"]
        #   reff = "1.2"
        #   -> [[("book", "1"), ("line", "2")], ...]
        mapped = list(zip_longest(
            map(attrgetter("name"), self.citations),
            reff.split("."),
        ))
        ancestors, leaf = mapped[:-1], mapped[-1]
        if ancestors:
            # set up parents and get leaf parent
            ancestor_cache = self.ancestor_cache
            prefix = ""
            last_ancestor = self.root
            for (label, num) in ancestors:
                key = f"{prefix}.{num}"
                try:
                    parent = ancestor_cache[key]
                except KeyError:
                    parent = RefNode(label=label, num=num, parent=last_ancestor)
                    ancestor_cache[key] = parent
                prefix += num
                last_ancestor = parent
        else:
            parent = self.root
        # create leaf ref
        RefNode(label=leaf[0], num=leaf[1], parent=parent)

    def lookup(self, path):
        return self.num_resolver.get(self.root, path)

    def chunk_config(self):
        # following was copied from scheme_grouper in Leipzig's CTS Nemo instance
        # https://github.com/OpenGreekAndLatin/cts_leipzig_ui/blob/master/cts_leipzig_ui/__init__.py#L69
        # @@@ consider how we might store the chunking config in the database
        labels = [citation.name for citation in self.citations]
        level = len(labels)
        groupby = 5
        if "word" in labels:
            labels = labels[:labels.index("word")]
        if str(self.urn) == "urn:cts:latinLit:stoa0040.stoa062.opp-lat1":
            level, groupby = 1, 2
        elif labels == ["book", "poem", "line"]:
            level, groupby = 2, 1
        elif labels == ["book", "line"]:
            level, groupby = 2, 30
        elif labels == ["book", "chapter"]:
            level, groupby = 2, 1
        elif labels == ["book"]:
            level, groupby = 1, 1
        elif labels == ["line"]:
            level, groupby = 1, 30
        elif labels == ["chapter", "section"]:
            level, groupby = 2, 2
        elif labels == ["chapter", "mishnah"]:
            level, groupby = 2, 1
        elif labels == ["chapter", "verse"]:
            level, groupby = 2, 1
        elif "line" in labels:
            groupby = 30
        return level, groupby

    def chunks(self, node=None):
        level, groupby = self.chunk_config()
        sorted_level = sorted(self.depth_iter(level - 1, node=node), key=methodcaller("sort_key"))
        grouped = itertools.groupby(sorted_level, key=methodcaller("sort_key", ancestors_only=True))
        for group in map(itemgetter(1), grouped):
            for chunk in chunker(group, groupby):
                start, end = chunk[0], chunk[-1]
                if start.num == end.num:
                    yield RefChunk(self.urn, start=start)
                else:
                    yield RefChunk(self.urn, start=start, end=end)

    def depth_iter(self, depth, node=None):
        if node is None:
            node = self.root
        return RefTreeDepthIter(node, depth)


class RefNode(anytree.NodeMixin):

    separator = "."

    def __init__(self, label=None, num=None, parent=None):
        self.label = label
        self.num = num
        self.parent = parent

    def __str__(self):
        return self.reference

    def __repr__(self):
        if self.is_root:
            return f"<RefRootNode>"
        else:
            return f"<RefNode {self.reference}>"

    @property
    def reference(self):
        if self.is_root:
            return ""
        bits = []
        for ancestor in self.ancestors[1:]:
            bits.append(ancestor.num)
        bits.append(self.num)
        return ".".join(bits)

    def sort_key(self, ancestors_only=False):
        if ancestors_only:
            return natural_keys(self.parent.reference)
        else:
            return natural_keys(self.reference)


class RefChunk:

    def __init__(self, urn, start, end=None):
        self.passage_urn = urn
        self.start, self.end = start, end

    def __repr__(self):
        return f"<RefChunk {self.urn}>"

    @property
    def urn(self):
        if self.end is None:
            return f"{self.passage_urn}:{self.start.reference}"
        return f"{self.passage_urn}:{self.start.reference}-{self.end.reference}"


def atoi(s):
    return int(s) if s.isdigit() else s


def natural_keys(s):
    return tuple([atoi(c) for c in re.split(r"(\d+)", s)])


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]


class CTS:
    """
    Thin-wrapper around calling into MyCapytain library. This class provides
    domain-specific implementations.
    """

    cache = {}

    def __init__(self):
        self.retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        self.resolver = HttpCtsResolver(self.retriever)

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
        r = self.resolver.getMetadata(str(urn))
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

    def fetch_text_inventory(self):
        if getattr(settings, "CTS_LOCAL_TEXT_INVENTORY", None) is not None:
            with open(settings.CTS_LOCAL_TEXT_INVENTORY, "r") as fp:
                return fp.read()
        else:
            return self.retriever.getCapabilities()

    def text_inventory(self):
        if self.cache.get("ti") is None:
            self.cache["ti"] = XmlCtsTextInventoryMetadata.parse(self.fetch_text_inventory())
        return self.cache["ti"]

    def resources(self, urn=None):
        key = urn
        if key in self.cache:
            return self.cache[key]
        else:
            if urn:
                urn = URN(urn)
            ti = self.text_inventory()
            if urn:
                ti = [x for x in [ti] + ti.descendants if x.id == str(urn)][0]
            resources = []
            members = sorted(ti.members, key=attrgetter("id"))
            for o in members:
                resource = Resource(
                    urn=o.id,
                    label=o.get_label(lang="eng"),
                    readable=o.readable,
                )
                resources.append(resource)
            self.cache[key] = resources
            return resources

    def passage(self, urn):
        return Passage(urn)


class Passage:

    cache = {}

    def __init__(self, urn):
        self.retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
        self.resolver = HttpCtsResolver(self.retriever)
        self.urn = URN(urn)
        self.base_urn = self.urn.upTo(URN.NO_PASSAGE)

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._metadata = self.resolver.getMetadata(self.urn.upTo(URN.NO_PASSAGE))
        return self._metadata

    @property
    def textual_node(self):
        if not hasattr(self, "_textual_node"):
            self._textual_node = self.resolver.getTextualNode(self.urn)
        return self._textual_node

    @property
    def lang(self):
        return self.metadata.lang

    @property
    def rtl(self):
        return self.lang in {"heb", "fa"}

    def toc(self):
        key = f"toc-{self.urn}"
        if key not in self.cache:
            depth = len(self.metadata.citation)
            tree = RefTree(self.urn.upTo(URN.NO_PASSAGE), self.metadata.citation)
            for reff in self.resolver.getReffs(self.urn, level=depth):
                tree.add(reff)
            self.cache[key] = tree
        return self.cache[key]

    @property
    def first_urn(self):
        chunk = next(self.toc().chunks(), None)
        if chunk is not None:
            return chunk.urn

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
