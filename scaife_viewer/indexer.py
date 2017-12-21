import json
from collections import deque
from itertools import chain, islice, zip_longest
from operator import attrgetter
from typing import Iterable

from anytree.iterators import PreOrderIter

from . import cts


class Indexer:

    def __init__(self, executor, pusher, urn_prefix=None, chunk_size=100, limit=None, dry_run=False):
        self.executor = executor
        self.pusher = pusher
        self.urn_prefix = urn_prefix
        self.chunk_size = chunk_size
        self.limit = limit
        self.dry_run = dry_run

    def index(self):
        cts.TextInventory.load()
        print("Text inventory loaded")
        if self.urn_prefix:
            print(f"Applying URN prefix filter: {self.urn_prefix}")
        with self.executor as executor:
            urns = chain.from_iterable(
                executor.map(
                    self.passage_urns_from_text,
                    self.texts(),
                    chunksize=100,
                )
            )
            if self.limit is not None:
                urns = islice(urns, self.limit)
            urns = list(urns)
            print(f"Indexing {len(urns)} passages")
            consume(executor.map(self.indexer, chunker(urns, self.chunk_size), chunksize=10))

    def texts(self):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    if self.urn_prefix and not str(text.urn).startswith(self.urn_prefix):
                        continue
                    yield text

    def passage_urns_from_text(self, text):
        urns = []
        try:
            toc = text.toc()
        except Exception as e:
            print(f"{text.urn} toc error: {e}")
        else:
            for node in PreOrderIter(toc.root, filter_=attrgetter("is_leaf")):
                urns.append(f"{text.urn}:{node.reference}")
        return urns

    def indexer(self, chunk: Iterable[str]):
        for urn in chunk:
            try:
                passage = cts.passage(urn)
            except cts.PassageDoesNotExist:
                print(f"Passage {urn} does not exist")
                continue
            except Exception as e:
                print(f"Error {e}")
                continue
            doc = self.passage_to_doc(passage)
            if not self.dry_run:
                self.pusher.push(doc)

    def passage_to_doc(self, passage):
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
            "content": passage.content,  # CPU intensive
        }

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["executor"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.executor = None


def consume(it):
    deque(it, maxlen=0)


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]


class DirectPusher:
    pass


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
