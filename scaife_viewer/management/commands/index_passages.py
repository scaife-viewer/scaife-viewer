import concurrent.futures
import contextlib
import cProfile
import json
import os
import pstats
import time
from collections import deque
from decimal import Decimal
from functools import partial
from itertools import chain, islice, zip_longest
from operator import attrgetter
from typing import Iterable

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from anytree.iterators import PreOrderIter

from ... import cts


class Command(BaseCommand):

    help = "Indexes passages in Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-workers",
            type=int,
            default=None,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
        )
        parser.add_argument("--urn-prefix")
        parser.add_argument("--chunk-size", type=int, default=100)
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--delete-index", action="store_true", default=False)

    def handle(self, *args, **options):
        max_workers = options["max_workers"]
        dry_run = options["dry_run"]
        urn_prefix = options["urn_prefix"]
        limit = options["limit"]
        delete_index = options["delete_index"]

        with CodeTimer() as timer:
            self.index_texts(
                max_workers,
                dry_run,
                urn_prefix,
                limit,
                options["chunk_size"],
                delete_index,
            )
        elapsed = timer.elapsed.quantize(Decimal("0.00"))
        print(f"Finished in {elapsed}s")

    def index_texts(self, num_workers, dry_run, urn_prefix, limit, chunk_size, delete_index):
        if not dry_run:
            if delete_index:
                delete_es_index()
            create_es_index()
        cts.TextInventory.load()
        print("Text inventory loaded")
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            if urn_prefix:
                print(f"Applying URN prefix filter: {urn_prefix}")
            urns = chain.from_iterable(executor.map(passage_urns_from_text, self.texts(urn_prefix), chunksize=100))
            if limit:
                urns = islice(urns, limit)
            urns = list(urns)
            print(f"Indexing {len(urns)} passages")
            indexer = partial(index_text_chunk, dry_run=dry_run)
            consume(executor.map(indexer, chunker(urns, chunk_size)))

    def texts(self, urn_prefix):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    if urn_prefix and not str(text.urn).startswith(urn_prefix):
                        continue
                    yield text


def consume(it):
    deque(it, maxlen=0)


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]


def passage_urns_from_text(text):
    urns = []
    try:
        toc = text.toc()
    except Exception as e:
        print(f"{text.urn} toc error: {e}")
    else:
        for node in PreOrderIter(toc.root, filter_=attrgetter("is_leaf")):
            urns.append(f"{text.urn}:{node.reference}")
    return urns


def es_index_exists():
    index_name = "scaife-viewer"
    r = requests.get(**es_req_kwargs(f"/{index_name}"))
    return r.ok


def delete_es_index():
    index_name = "scaife-viewer"
    if es_index_exists():
        requests.delete(**es_req_kwargs(f"/{index_name}"))


def create_es_index():
    index_name = "scaife-viewer"
    doc_type = "text"

    if not es_index_exists():
        payload = {
            "mappings": {
                doc_type: {
                    "properties": {
                        "urn": {
                            "type": "keyword",
                        },
                        "text_group": {
                            "type": "keyword",
                        },
                        "work": {
                            "type": "keyword",
                        },
                        "content": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                            "store": True,
                            "analyzer": "fulltext_analyzer",
                        },
                    },
                },
            },
            "settings": {
                "index": {
                    "number_of_shards": 5,
                    "number_of_replicas": 0,
                },
                "analysis": {
                    "analyzer": {
                        "fulltext_analyzer": {
                            "type": "custom",
                            "tokenizer": "icu_tokenizer",
                            "filter": [
                                "icu_folding",
                            ],
                        },
                    },
                },
            },
        }
        r = requests.put(**es_req_kwargs(
            f"/{index_name}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        ))
        if r.status_code >= 400 and r.status_code < 500:
            raise Exception(r.json())
        r.raise_for_status()


def log(msg):
    pid = os.getpid()
    print(f"[pid={pid}] {msg}")


def index_text_chunk(chunk: Iterable[str], dry_run: bool):
    index_name = "scaife-viewer"
    doc_type = "text"
    docs = []

    for urn in chunk:
        try:
            passage = cts.passage(urn)
        except cts.PassageDoesNotExist:
            print(f"Passage {urn} does not exist")
            continue
        except Exception as e:
            print(f"Error {e}")
            continue
        doc = {
            "urn": urn,
            "text_group": str(passage.text.urn.upTo(cts.URN.TEXTGROUP)),
            "work": str(passage.text.urn.upTo(cts.URN.WORK)),
            "text": {
                "urn": str(passage.text.urn),
                "label": passage.text.label,
                "description": passage.text.description,
            },
            "reference": str(passage.reference),
            "content": passage.content,
        }
        docs.append(doc)

    if not dry_run:
        lines = []
        for doc in docs:
            lines.extend([
                json.dumps({
                    "index": {
                        "_index": index_name,
                        "_type": doc_type,
                        "_id": doc["urn"],
                    },
                }),
                json.dumps(doc),
            ])
        lines.append("")
        r = requests.post(
            **es_req_kwargs(
                "/_bulk",
                data="\n".join(lines).encode("utf-8"),
                headers={
                    "Content-Type": "application/x-ndjson",
                },
            ),
        )
        if r.status_code == 400:
            print(r.json())
        r.raise_for_status()

    # log(f"Indexed {len(docs)} passages")


def es_req_kwargs(path, **kwargs):
    kwargs["url"] = f"{settings.ELASTICSEARCH_URL}{path}"
    return kwargs


class CodeTimer:

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, typ, value, traceback):
        self.elapsed = Decimal.from_float(time.perf_counter() - self.start)


@contextlib.contextmanager
def profile(*args, **kwargs):
    profile = cProfile.Profile(*args, **kwargs)
    profile.enable()
    yield
    profile.disable()
    ps = pstats.Stats(profile)
    ps.sort_stats("time", "cumulative").print_stats(.1)
