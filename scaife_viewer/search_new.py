from operator import itemgetter

from django.conf import settings
from django.urls import reverse

import regex
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as scanner

from . import cts


es = Elasticsearch(
    hosts=settings.ELASTICSEARCH_HOSTS
)

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
            "number_of_fragments": 0,
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
    final = []
    for hit in results["hits"]["hits"]:
        cts_passage = cts.passage(hit["_id"])
        highlight_kind = hit["highlight"].get("content", [""])[0]
        if kind == "lemma":
            highlight_kind = hit["highlight"].get("lemma_content", [""])[0]
        highlighter = Highlighter(cts_passage, highlight_kind)
        test = highlighter.fragments()
        final.append(
            {
              "passage":  cts_passage,
              "link": reverse("reader", kwargs={"urn":  cts_passage.urn}),
              "content": highlighter.fragments()
            }
        )
    return final


# def filtered_text_groups(self):
#     buckets = []
#     for bucket in self.response["aggregations"]["filtered_text_group"]["buckets"]:
#         buckets.append({
#             "text_group": cts.collection(bucket["key"]),
#             "count": bucket["doc_count"],
#         })
#     return sorted(buckets, key=itemgetter("count"), reverse=True)



class SearchResult:

    def __init__(self, hit):
        self.hit = hit
        self.passage = cts.passage(hit["_id"])
        self.link_urn = self.passage.urn  # @@@ consider dynamically chunking and giving a better passage URN
        self.content_highlights = hit["highlight"].get("content", [""])[0]
        self.lemma_highlights = hit["highlight"].get("lemma_content", [""])[0]
        self.highlighter = Highlighter(
            self.passage,
            self.content_highlights if self.content_highlights else self.lemma_highlights,
        )
        self.sort_idx = hit["_source"]["sort_idx"]

    def __getitem__(self, key):
        missing = object()
        value = getattr(self, key, missing)
        if value is missing:
            raise KeyError(key)
        return value

    @property
    def content(self):
        return self.highlighter.fragments()

    @property
    def highlights(self):
        return self.highlighter.tokens()

    @property
    def link(self):
        return reverse("reader", kwargs={"urn": self.link_urn})


w_re = regex.compile(fr"(?:<em>)?(?:\w[-\w]*|{chr(0xfffd)})(?:</em>)?")


class Highlighter:

    def __init__(self, passage, highlights):
        self.passage = passage
        self.highlights = highlights

    def tokens(self):
        if not hasattr(self, "_tokens"):
            acc = set()
            it = zip(
                self.highlights.split(" "),
                [(t["w"], t["i"]) for t in self.passage.tokenize(whitespace=False)]
            )
            for hw, (sw, si) in it:
                if hw:
                    if w_re.match(hw):
                        if "<em>" in hw:
                            acc.add((sw, si))
            self._tokens = acc
        return self._tokens

    def content(self):
        if not hasattr(self, "_content"):
            acc = []
            highlighted_tokens = self.tokens()
            for token in self.passage.tokenize():
                if (token["w"], token["i"]) in highlighted_tokens:
                    acc.extend(["<em>", token["w"], "</em>"])
                else:
                    acc.append(token["w"])
            self._content = "".join(acc)
        return self._content

    def fragments(self, context=5):
        content = self.content()
        L = content.split(" ")
        acc = []
        for i, w in enumerate(L):
            fragment = []
            if regex.match(r"</?em>", w):
                fragment.extend(L[max(0, i - context):i])
                fragment.append(w)
                fragment.extend(L[i + 1:i + context + 1])
                acc.append(" ".join(fragment))
        return acc
