import json
from collections import deque
from itertools import zip_longest
from operator import attrgetter
from typing import Iterable

import dask.bag
import elasticsearch
import elasticsearch.helpers
from anytree.iterators import PreOrderIter

from . import cts
from .morphology import Morphology


morphology = None


class Indexer:

    def __init__(self, pusher, morphology_path, urn_prefix=None, chunk_size=100, limit=None, dry_run=False):
        self.pusher = pusher
        self.urn_prefix = urn_prefix
        self.chunk_size = chunk_size
        self.limit = limit
        self.dry_run = dry_run
        self.load_morphology(morphology_path)

    def load_morphology(self, path):
        global morphology
        if path and morphology is None:
            morphology = Morphology.load(path)
            print("Morphology loaded")

    def index(self):
        cts.TextInventory.load()
        print("Text inventory loaded")
        if self.urn_prefix:
            urn_prefix = cts.URN(self.urn_prefix)
            print(f"Applying URN prefix filter: {urn_prefix.upTo(cts.URN.NO_PASSAGE)}")
        else:
            urn_prefix = None
        texts = dask.bag.from_sequence(
            self.texts(
                urn_prefix.upTo(cts.URN.NO_PASSAGE) if urn_prefix else None
            )
        )
        passages = texts.map(self.passages_from_text).flatten()
        if urn_prefix and urn_prefix.reference:
            print(f"Applying URN reference filter: {urn_prefix.reference}")
            passages = passages.filter(lambda p: p["urn"] == str(urn_prefix))
        if self.limit is not None:
            passages = passages.take(self.limit, npartitions=-1)
        else:
            passages = passages.compute()
        print(f"Indexing {len(passages)} passages")
        dask.bag.from_sequence(passages).map_partitions(self.indexer).compute()

    def texts(self, urn_prefix):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    if urn_prefix and not str(text.urn).startswith(urn_prefix):
                        continue
                    yield text

    def passages_from_text(self, text):
        passages = []
        try:
            toc = text.toc()
        except Exception as e:
            print(f"{text.urn} toc error: {e}")
        else:
            leaves = PreOrderIter(toc.root, filter_=attrgetter("is_leaf"))
            for i, node in enumerate(leaves):
                passages.append({
                    "urn": f"{text.urn}:{node.reference}",
                    "sort_idx": i,
                })
        return passages

    def indexer(self, chunk: Iterable[str]):
        for p in chunk:
            urn = p["urn"]
            try:
                passage = cts.passage(urn)
            except cts.PassageDoesNotExist:
                print(f"Passage {urn} does not exist")
                continue
            except Exception as e:
                print(f"Error {e}")
                continue
            doc = self.passage_to_doc(passage, p["sort_idx"])
            if not self.dry_run:
                self.pusher.push(doc)

    def lemma_content(self, passage) -> str:
        if morphology is None:
            return ""
        short_key = morphology.short_keys.get(str(passage.text.urn))
        if short_key is None:
            return ""
        thibault = [t["w"] for t in passage.tokenize(whitespace=False)]
        giuseppe = []
        text = morphology.text.get((short_key, str(passage.reference)))
        if text is None:
            return ""
        for form_keys in text.values():
            form_key = form_keys[0]
            form = morphology.forms[int(form_key) - 1]
            giuseppe.append((form.form, form.lemma))
        missing = chr(0xfffd)
        return " ".join([
            {None: missing}.get(w, w)
            for w in align_text(thibault, giuseppe)
        ])

    def passage_to_doc(self, passage, sort_idx):
        return {
            "urn": str(passage.urn),
            "text_group": str(passage.text.urn.upTo(cts.URN.TEXTGROUP)),
            "work": str(passage.text.urn.upTo(cts.URN.WORK)),
            "text": {
                "urn": str(passage.text.urn),
                "label": passage.text.label,
                "description": passage.text.description,
            },
            "reference": str(passage.reference),
            "sort_idx": sort_idx,
            "lemma_content": self.lemma_content(passage),
            "content": " ".join([t["w"] for t in passage.tokenize(whitespace=False)]),
        }


def consume(it):
    deque(it, maxlen=0)


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]


class DirectPusher:

    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size
        self.index_name = "scaife-viewer"
        self.es.indices.create(index=self.index_name, ignore=400)

    @property
    def es(self):
        if not hasattr(self, "_es"):
            self._es = elasticsearch.Elasticsearch()
        return self._es

    @property
    def docs(self):
        if not hasattr(self, "_docs"):
            self._docs = deque(maxlen=self.chunk_size)
        return self._docs

    def push(self, doc):
        self.docs.append(doc)
        if len(self.docs) == self.chunk_size:
            self.commit_docs()

    def commit_docs(self):
        metadata = {
            "_op_type": "index",
            "_index": self.index_name,
            "_type": "text",
        }
        docs = ({"_id": doc["urn"], **metadata, **doc} for doc in self.docs)
        elasticsearch.helpers.bulk(self.es, docs)
        self.docs.clear()

    def __getstate__(self):
        s = self.__dict__.copy()
        if "_es" in s:
            del s["_es"]
        if "_docs" in s:
            del s["_docs"]
        return s


class PubSubPusher:

    def __init__(self, project, topic):
        self.topic_path = f"projects/{project}/topics/{topic}"

    @property
    def publisher(self):
        if not hasattr(self, "_publisher"):
            # import happens here because module-level kicks off the
            # thread to handle publishing (which breaks multiprocessing)
            import google.cloud.pubsub
            self._publisher = google.cloud.pubsub.PublisherClient()
        return self._publisher

    def push(self, doc):
        self.publisher.publish(self.topic_path, json.dumps(doc).encode("utf-8"))

    def __getstate__(self):
        s = self.__dict__.copy()
        if "_publisher" in s:
            del s["_publisher"]
        return s


def nw_align(a, b, replace_func=lambda x, y: -1 if x != y else 0, insert=-1, delete=-1):
    ZERO, LEFT, UP, DIAGONAL = 0, 1, 2, 3
    len_a, len_b = len(a), len(b)
    matrix = [[(0, ZERO) for x in range(len_b + 1)] for y in range(len_a + 1)]
    for i in range(len_a + 1):
        matrix[i][0] = (insert * i, UP)
    for j in range(len_b + 1):
        matrix[0][j] = (delete * j, LEFT)
    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            replace = replace_func(a[i - 1], b[j - 1])
            matrix[i][j] = max([
                (matrix[i - 1][j - 1][0] + replace, DIAGONAL),
                (matrix[i][j - 1][0] + insert, LEFT),
                (matrix[i - 1][j][0] + delete, UP)
            ])
    i, j = len_a, len_b
    alignment = []
    while (i, j) != (0, 0):
        if matrix[i][j][1] == DIAGONAL:
            alignment.insert(0, (a[i - 1], b[j - 1]))
            i -= 1
            j -= 1
        elif matrix[i][j][1] == LEFT:
            alignment.insert(0, (None, b[j - 1]))
            j -= 1
        else:  # UP
            alignment.insert(0, (a[i - 1], None))
            i -= 1
    return alignment


def replace_func(a, b):
    if a == b[0]:
        return 0
    else:
        return -1


def align_text(a, b):
    result = nw_align(a, b, replace_func=replace_func)
    for x, y in result:
        if y is None:
            yield None
        elif x:
            yield y[1]
