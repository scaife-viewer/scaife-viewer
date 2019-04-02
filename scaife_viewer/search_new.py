from operator import itemgetter

from django.conf import settings
from django.urls import reverse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as scanner

from . import cts
from .utils import apify


es = Elasticsearch(
    hosts=settings.ELASTICSEARCH_HOSTS
)

# TODO: add sniff_on_start and sniff_on_connection_fail to environment variables
# es = Elasticsearch(
#     hosts=settings.ELASTICSEARCH_HOSTS,
#     sniff_on_start=True,
#     sniff_on_connection_fail=True,
# )


def create_query(q, query_fields, scope):
    sq = {
        "simple_query_string": {
            "query": q,
            "fields": query_fields,
            "default_operator": "and",
        }
    }
    if scope:
        body = {
            "bool": {
                "must": sq,
                "filter": {"term": scope},
            },
        }
    else:
        body = sq
    return body


def get_search_results(q, scope=None, aggregate_field=None, kind="form", fragments=1000, size=10, offset=0):
    highlight_fields = {"content": {}}
    query_fields = ["content"]
    if kind == "lemma":
        highlight_fields = {"lemma_content": {}}
        query_fields = ["lemma_content"]
    query_dict = create_query(q, query_fields, scope)
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
    sort = [{"sort_idx": "asc"}]
    body = {
        "highlight": {
            "type": "plain",
            "number_of_fragments": fragments,
            "fragment_size": 60,
            "fields": highlight_fields,
        },
        "query": query_dict,
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
        highlight_kind = hit["highlight"].get("content", [""])
        if kind == "lemma":
            highlight_kind = hit["highlight"].get("lemma_content", [""])
        final.append(
            {
                "passage": apify(cts_passage, with_content=False),
                "link": reverse("reader", kwargs={"urn": cts_passage.urn}),
                "content": highlight_kind
            }
        )
    return {
        "results": final,
        "text_groups": text_groups,
        "total_count": results["hits"]["total"]
    }


def scan(q, kind, scope):
    query_fields = ["content"]
    if kind == "lemma":
        query_fields = ["lemma_content"]
    query_dict = create_query(q, query_fields, scope)
    return scanner(
        es,
        query={
            "query": query_dict,
            "sort": [{"sort_idx": "asc"}],
            "_source": False,
        },
        preserve_order=bool("document"),
        raise_on_error=False,
    )


def create_buckets(data):
    buckets = []
    for bucket in data:
        buckets.append({
            "text_group": cts.collection(bucket["key"]).as_json(),
            "count": bucket["doc_count"],
        })
    return sorted(buckets, key=itemgetter("count"), reverse=True)
