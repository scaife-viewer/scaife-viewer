import concurrent.futures
import json
import timeit
from decimal import Decimal
from functools import partial
from itertools import chain, zip_longest
from operator import attrgetter
from typing import Iterable

from django.core.management.base import BaseCommand

import requests
from anytree.iterators import PreOrderIter

from ... import cts


class Command(BaseCommand):

    help = "Indexes all texts in Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--workers",
            type=int,
            default=None,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
        )
        parser.add_argument("--urn-filter")
        parser.add_argument("--chunk-size", type=int, default=100)

    def handle(self, *args, **options):
        num_workers = options["workers"]
        dry_run = options["dry_run"]
        urn_filter = options["urn_filter"]

        if not dry_run:
            create_es_index()

        cts.TextInventory.load()
        print("Text inventory loaded")

        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            if urn_filter:
                print(f"Applying URN filter: {urn_filter}")
            urns = list(chain.from_iterable(executor.map(
                passage_urns_from_text,
                self.texts(urn_filter),
                chunksize=100,
            )))
            print(f"Indexing {len(urns)} passages")
            list(executor.map(
                partial(index_text_chunk, dry_run=dry_run),
                chunker(urns, options["chunk_size"]),
                chunksize=1,
            ))

    def texts(self, urn_filter):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    if urn_filter and not str(text.urn).startswith(urn_filter):
                        continue
                    yield text


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


def create_es_index():
    index_name = "scaife-viewer"
    doc_type = "text"

    r = requests.get(**es_req_kwargs(f"/{index_name}"))
    if r.status_code == 404:
        payload = {
            "mappings": {
                doc_type: {
                    "properties": {
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
                            "tokenizer": "standard",  # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-standard-tokenizer.html
                        },
                    },
                },
            },
        }
        r = requests.put(**es_req_kwargs(
            f"/{index_name}",
            data=json.dumps(payload),
        ))
        r.raise_for_status()


def index_text_chunk(chunk: Iterable[str], dry_run: bool):
    index_name = "scaife-viewer"
    doc_type = "text"
    docs = []

    for urn in chunk:
        passage = cts.passage(urn)
        doc = {
            "urn": urn,
            "text": {
                "urn": str(passage.text.urn),
                "label": passage.text.label,
                "description": passage.text.description,
            },
            "reference": str(passage.reference),
            "content": passage.textual_node().export(exclude=["tei:teiHeader"]),
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

    # print(f"Indexed {len(docs)} passages")


def es_req_kwargs(path, **kwargs):
    kwargs["url"] = f"http://localhost:9200{path}"
    return kwargs
