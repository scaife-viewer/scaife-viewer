from operator import itemgetter

from django.conf import settings
from django.urls import reverse

import regex
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as scanner

from . import cts
from .utils import apify


es = Elasticsearch(
    hosts=settings.ELASTICSEARCH_HOSTS
)



# TODO: refactor into a class!
def simple_search(q, scope=None, aggregate_field=None, kind="form", size=10, offset=0, sort_by=None):
    highlight_fields = {"content": {}}
    query_fields = ["content"]
    if kind == "lemma":
        highlight_fields = {"lemma_content": {}}
        query_fields = ["lemma_content"]
    sq = {
        "simple_query_string": {
            "query": q,
            "fields": query_fields,
            "default_operator": "and",
        }
    }
    if scope:
        q = {
            "bool": {
                "must": sq,
                "filter": {"term": scope},
            },
        }
    else:
        q = sq
    query_args = {}
    if aggregate_field:
        query_args = {
            f"filtered_{aggregate_field}": {
                "terms": {
                    "field": aggregate_field,
                    "size": 300,
                },
            },
        }
    sort = {}
    if sort_by:
        sort = [{"sort_idx": "asc"}]
    body = {
        "highlight": {
            "type": "fvh",
            "number_of_fragments": 1000,
            "fragment_size": 50,
            "fields": highlight_fields,
        },
        "query": q,
        "aggs": query_args,
        "sort": sort
    }
    results = es.search(
        index="scaife-viewer",
        doc_type="text",
        body=body,
        size=size,
        from_=offset,
    )
    text_groups = create_buckets(results["aggregations"]["filtered_text_group"]["buckets"])
    final = []
    for hit in results["hits"]["hits"]:
        cts_passage = cts.passage(hit["_id"])
        highlight_kind = hit["highlight"].get("content", [""])[0]
        if kind == "lemma":
            highlight_kind = hit["highlight"].get("lemma_content", [""])[0]
        final.append(
            {
              "passage": apify(cts_passage, with_content=False),
              "link": reverse("reader", kwargs={"urn":  cts_passage.urn}),
              "content": highlight_kind
            }
        )
    return {
        "results": final,
        "text_groups": text_groups,
        "total_count": results["hits"]["total"]
    }


def create_buckets(data):
    buckets = []
    for bucket in data:
        buckets.append({
            "text_group": cts.collection(bucket["key"]).as_json(),
            "count": bucket["doc_count"],
        })
    return sorted(buckets, key=itemgetter("count"), reverse=True)
