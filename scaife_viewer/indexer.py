import json
from collections import deque
from itertools import chain, islice, zip_longest
from operator import attrgetter
from typing import Iterable

import dask.bag
import elasticsearch
import elasticsearch.helpers
from anytree.iterators import PreOrderIter

from . import cts
from .morphology import Morphology


class Indexer:

    def __init__(self, pusher, morphology_path, urn_prefix=None, chunk_size=100, limit=None, dry_run=False):
        self.pusher = pusher
        self.urn_prefix = urn_prefix
        self.chunk_size = chunk_size
        self.limit = limit
        self.dry_run = dry_run
        self.morphology_path = morphology_path

    def index(self):
        cts.TextInventory.load()
        print("Text inventory loaded")
        if self.urn_prefix:
            print(f"Applying URN prefix filter: {self.urn_prefix}")
        passages = chain.from_iterable(
            dask.bag.from_sequence(self.texts()).map(self.passages_from_text)
        )
        if self.limit is not None:
            passages = islice(passages, self.limit)
        passages = list(passages)
        print(f"Indexing {len(passages)} passages")
        dask.bag.from_sequence(passages).map_partitions(self.indexer).compute()

    def texts(self):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    if self.urn_prefix and not str(text.urn).startswith(self.urn_prefix):
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

    def offset_iter(self, tokens):
        i = 1
        for token in tokens:
            yield i, token
            if token["t"] != "s":
                i += 1

    def lemma_content(self, passage):
        if not self.morphology_path:
            return ""
        if not hasattr(self, "morphology"):
            self.morphology = Morphology.load(self.morphology_path)
        short_key = self.morphology.short_keys.get(str(passage.text.urn))
        if short_key is None:
            return ""
        lemmas = []
        missing = chr(0x2593)
        for i, token in self.offset_iter(passage.tokenize()):
            if token["t"] == "w":
                text_key = (short_key, str(passage.reference), str(i))
                form_key = self.morphology.text.get(text_key)
                if form_key is None:
                    lemmas.append(missing)
                else:
                    try:
                        form = self.morphology.forms[int(form_key)]
                    except IndexError:
                        lemmas.append(missing)
                    else:
                        lemmas.append(form.lemma)
            else:
                lemmas.append(token["w"])
        return "".join(lemmas)

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
            "content": passage.content,
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
