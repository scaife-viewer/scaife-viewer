from collections import defaultdict
from operator import itemgetter

from django.conf import settings
from django.core.urlresolvers import reverse

import regex
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as scanner

from . import cts


es = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])


class SearchQuery:

    def __init__(self, q, scope=None, sort_by=None, highlight_fragments=5, aggregate_field=None):
        self.q = q
        self.scope = {} if scope is None else scope
        self.sort_by = sort_by
        self.highlight_fragments = highlight_fragments
        self.aggregate_field = aggregate_field
        self.total_count = None

    def query_index(self):
        return {
            "index": "scaife-viewer",
            "doc_type": "text",
        }

    def query_sort(self):
        if not self.sort_by:
            return {}
        if self.sort_by == "document":
            return {"sort": [{"sort_idx": "asc"}]}

    def query_aggs(self):
        if not self.aggregate_field:
            return {}
        return {
            "aggs": {
                f"filtered_{self.aggregate_field}": {
                    "terms": {
                        "field": self.aggregate_field,
                        "size": 300,
                    },
                },
            },
        }

    def query(self):
        q = {}
        sq = {
            "simple_query_string": {
                "query": self.q,
                "fields": ["content"],
                "default_operator": "and",
            }
        }
        if self.scope:
            q = {
                "bool": {
                    "must": sq,
                    "filter": {"term": self.scope},
                },
            }
        else:
            q = {**sq}
        return q

    def search_kwargs(self, size=10, offset=0):
        return {
            "body": {
                **self.query_sort(),
                "highlight": {
                    "fields": {
                        "content": {
                            "type": "fvh",
                            "number_of_fragments": self.highlight_fragments,
                        },
                    },
                },
                "query": self.query(),
                **self.query_aggs(),
            },
            "size": size,
            "from_": offset,
            **self.query_index()
        }

    def search_window(self, **kwargs):
        return SearchResultSet(es.search(**self.search_kwargs(**kwargs)))

    def __iter__(self):
        return iter(self.search_window())

    def count(self):
        if self.total_count is None:
            self.total_count = es.count(**{
                "body": {"query": self.query()},
                **self.query_index()
            })["count"]
        return self.total_count

    def scan(self):
        return scanner(
            es,
            query={
                **self.query_sort(),
                "_source": False,
                "query": self.query(),
            },
            preserve_order=bool(self.sort_by),
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            size = len(range(*key.indices(self.total_count)))
            return self.search_window(size=size, offset=key.start)
        raise NotImplementedError()


class SearchResultSet:

    def __init__(self, response):
        self.response = response

    def __iter__(self):
        for hit in self.response["hits"]["hits"]:
            yield self.result(hit)

    def result(self, hit):
        passage = cts.passage(hit["_id"])
        link_urn = passage.urn  # @@@ consider dynamically chunking and giving a better passage URN
        return {
            "passage": passage,
            "content": hit["highlight"]["content"],
            "highlights": extract_highlights(hit["highlight"]["content"][0]),
            "sort_idx": hit["_source"]["sort_idx"],
            "link": reverse("reader", kwargs={"urn": link_urn}),
        }

    def filtered_text_groups(self):
        buckets = []
        for bucket in self.response["aggregations"]["filtered_text_group"]["buckets"]:
            buckets.append({
                "text_group": cts.collection(bucket["key"]),
                "count": bucket["doc_count"],
            })
        return sorted(buckets, key=itemgetter("count"), reverse=True)


w = r"(?:<em>)?\w[-\w]*(?:</em>)?"
p = r"\p{P}+"
ws = r"[\p{Z}\s]+"
token_re = regex.compile(fr"{w}|{p}|{ws}")
w_re = regex.compile(w)


def extract_highlights(content):
    tokens = []
    idx = defaultdict(int)
    for w in token_re.findall(content):
        if w:
            highlighted = False
            if w_re.match(w):
                highlighted = "<em>" in w
                if highlighted:
                    w = regex.sub(r"</?em>", "", w)
            wl = len(w)
            for wk in (w[i:j + 1] for i in range(wl) for j in range(i, wl)):
                idx[wk] += 1
            if highlighted:
                tokens.append({"w": w, "i": idx[w]})
    return tokens
