import itertools
from itertools import zip_longest
from operator import attrgetter, itemgetter, methodcaller

import anytree

from .utils import chunker, natural_keys


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
            # MyCapytain bugish: citation name could be None (should always be a string)
            map(str, map(attrgetter("name"), self.citations)),
            reff.split("."),
        ))
        ancestors, leaf = mapped[:-1], mapped[-1]
        if ancestors:
            # set up parents and get leaf parent
            ancestor_cache = self.ancestor_cache
            prefix = ""
            last_ancestor = self.root
            for (label, num) in ancestors:
                key = f"{prefix}{num}"
                try:
                    parent = ancestor_cache[key]
                except KeyError:
                    parent = RefNode(label=label, num=num, parent=last_ancestor)
                    ancestor_cache[key] = parent
                prefix += f"{num}."
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
        grouped = itertools.groupby(
            self.depth_iter(level - 1, node=node),
            key=methodcaller("sort_key", ancestors_only=True),
        )
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

    @property
    def human_reference(self):
        if self.is_root:
            return ""
        bits = []
        for ancestor in self.ancestors[1:]:
            bits.append(f"{ancestor.label.title()} {ancestor.num}")
        bits.append(f"{self.label.title()} {self.num}")
        return " ".join(bits)

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
