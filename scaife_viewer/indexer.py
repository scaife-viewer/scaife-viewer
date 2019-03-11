import json
from collections import deque, Counter
from itertools import zip_longest
from operator import attrgetter
from typing import Iterable, List, NamedTuple

import dask.bag
import elasticsearch
import elasticsearch.helpers
from anytree.iterators import PreOrderIter

from django.conf import settings

from . import cts
from .morphology import Morphology


morphology = None


class SortedPassage(NamedTuple):

    urn: str
    sort_idx: int


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

    def get_urn_obj(self):
        if not self.urn_prefix:
            return None
        return cts.URN(self.urn_prefix)

    def get_urn_prefix_filter(self, urn_obj):
        if not urn_obj:
            return None
        if urn_obj.reference:
            up_to = cts.URN.NO_PASSAGE
        elif urn_obj.version:
            up_to = cts.URN.VERSION
        elif urn_obj.work:
            up_to = cts.URN.WORK
        elif urn_obj.textgroup:
            up_to = cts.URN.TEXTGROUP
        elif urn_obj.namespace:
            up_to = cts.URN.NAMESPACE
        else:
            raise ValueError(f'Could not derive prefix filter from "{urn_obj}"')

        value = urn_obj.upTo(up_to)
        print(f"Applying URN prefix filter: {value}")
        return value

    def index(self):
        cts.TextInventory.load()
        print("Text inventory loaded")
        urn_obj = self.get_urn_obj()
        prefix_filter = self.get_urn_prefix_filter(urn_obj)
        texts = dask.bag.from_sequence(
            self.texts(prefix_filter)
        )
        passages = texts.map(self.passages_from_text).flatten()
        if urn_obj and urn_obj.reference:
            print(f"Applying URN reference filter: {urn_obj.reference}")
            passages = passages.filter(lambda p: p.urn == str(urn_obj))
        if self.limit is not None:
            passages = passages.take(self.limit, npartitions=-1)
        else:
            passages = passages.compute()
        print(f"Indexing {len(passages)} passages")
        word_counts = dask.bag.from_sequence(passages).map_partitions(self.indexer).compute()
        total_word_counts = Counter()
        for (lang, count) in word_counts:
            total_word_counts[lang] += count
        word_count_line = [f"{lang}={count}" for lang, count in total_word_counts.items()]
        print("Word Count Summary: {0}".format(", ".join(word_count_line)))

    def texts(self, urn_prefix):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    # skip these URNs because they cause MemoryError due to their
                    # massive token size when doing morphology alignment
                    # @@@ proper exclude functionality
                    exclude = {
                        "urn:cts:greekLit:tlg2371.tlg001.opp-grc1",
                        "urn:cts:greekLit:tlg4013.tlg001.opp-grc1",
                        "urn:cts:greekLit:tlg4013.tlg003.opp-grc1",
                        "urn:cts:greekLit:tlg4013.tlg004.opp-grc1",
                        "urn:cts:greekLit:tlg4013.tlg005.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg001.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg002.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg004.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg005.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg006.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg007.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg008.opp-grc1",
                        "urn:cts:greekLit:tlg4015.tlg009.opp-grc1",
                    }
                    if str(text.urn) in exclude:
                        continue
                    if urn_prefix and not str(text.urn).startswith(urn_prefix):
                        continue
                    yield text

    def passages_from_text(self, text) -> List[SortedPassage]:
        passages = []
        try:
            toc = text.toc()
        except Exception as e:
            print(f"{text.urn} toc error: {e}")
        else:
            leaves = PreOrderIter(toc.root, filter_=attrgetter("is_leaf"))
            for i, node in enumerate(leaves):
                passages.append(SortedPassage(
                    urn=f"{text.urn}:{node.reference}",
                    sort_idx=i,
                ))
        return passages

    def indexer(self, chunk: Iterable[SortedPassage]):
        from raven.contrib.django.raven_compat.models import client as sentry
        words = []
        result = None
        for p in chunk:
            urn = p.urn
            try:
                passage = cts.passage(urn)
            except cts.PassageDoesNotExist:
                print(f"Passage {urn} does not exist")
                continue
            except Exception as e:
                print(f"Error {e}")
                continue
            try:
                # tokenized once and passed around as an optimization
                tokens = passage.tokenize(whitespace=False)
                words.append((str(passage.text.lang), self.count_words(tokens)))
                doc = self.passage_to_doc(passage, p.sort_idx, tokens)
            except MemoryError:
                return words
            except Exception:
                sentry.captureException()
                raise
            if not self.dry_run:
                result = self.pusher.push(doc)

        self.pusher.finalize(result, self.dry_run)

        return words

    def count_words(self, tokens) -> int:
        n = 0
        for token in tokens:
            if token["t"] == "w":
                n += 1
        return n

    def lemma_content(self, passage, tokens) -> str:
        if morphology is None:
            return ""
        short_key = morphology.short_keys.get(str(passage.text.urn))
        if short_key is None:
            return ""
        thibault = [token["w"] for token in tokens]
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

    def passage_to_doc(self, passage, sort_idx, tokens):
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
            "lemma_content": self.lemma_content(passage, tokens),
            "content": " ".join([token["w"] for token in tokens]),
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
            self._es = elasticsearch.Elasticsearch(
                hosts=settings.ELASTICSEARCH_HOSTS,
                sniff_on_start=True,
                sniff_on_connection_fail=True,
            )
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

    def finalize(self, result, dry_run):
        if dry_run:
            return

        # we need to ensure the deque is cleared if less than
        # `chunk_size`
        self.commit_docs()
        print("Committing documents to ElasticSearch")

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
        """
        Returns a Future

        https://github.com/googleapis/google-cloud-python/blob/master/pubsub/docs/publisher/index.rst#futures
        """
        return self.publisher.publish(self.topic_path, json.dumps(doc).encode("utf-8"))

    def finalize(self, future, dry_run):
        if dry_run:
            return

        if future and not future.done():
            print("Publishing messages to PubSub")
            # Block until the last message has been published
            # https://github.com/googleapis/google-cloud-python/blob/69ec9fea1026c00642ca55ca18110b7ef5a09675/pubsub/docs/publisher/index.rst#futures
            future.result()

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
