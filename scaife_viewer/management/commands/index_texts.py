import concurrent.futures
import json
import timeit
from decimal import Decimal
from itertools import zip_longest

from django.core.management.base import BaseCommand

import requests

from ... import cts


class Command(BaseCommand):

    help = "Indexes all texts in Elasticsearch"

    def handle(self, *args, **options):
        cts.TextInventory.load()
        print("text inventory loaded")
        chunks = chunker((str(text.urn) for text in self.texts()), 1)
        num_workers = None

        create_es_index()
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            for completed in executor.map(index_text_chunk, chunks):
                for urn, elapsed in completed:
                    duration = Decimal.from_float(elapsed).quantize(Decimal("0.00"))
                    print(f"indexed {urn} ({duration}s)")

    def texts(self):
        ti = cts.text_inventory()
        for text_group in ti.text_groups():
            for work in text_group.works():
                for text in work.texts():
                    yield text


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]


def create_es_index():
    index_name = "scaife-viewer"
    doc_type = "text"

    payload = {
        "mappings": {
            doc_type: {
                "properties": {
                    "text": {
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


def index_text_chunk(chunk):
    resolver = cts.default_resolver()
    urns = []
    index_name = "scaife-viewer"
    doc_type = "text"

    for urn in chunk:
        start_time = timeit.default_timer()
        text = cts.collection(urn)
        textual_node = resolver.getTextualNode(urn)
        raw_text = textual_node.export(exclude=["tei:teiHeader"])
        doc = {
            "urn": urn,
            "label": text.label,
            "description": text.description,
            "text": raw_text,
        }
        r = requests.put(
            **es_req_kwargs(
                f"/{index_name}/{doc_type}/{urn}",
                data=json.dumps(doc).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                },
            ),
        )
        r.raise_for_status()
        elapsed = timeit.default_timer() - start_time
        urns.append((urn, elapsed))

    return urns


def es_req_kwargs(path, **kwargs):
    kwargs["url"] = f"http://localhost:9200{path}"
    return kwargs
