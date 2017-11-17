from operator import itemgetter

from django.conf import settings
from django.core.urlresolvers import reverse

from elasticsearch import Elasticsearch

from . import cts


es = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])


class SearchQuery:

    def __init__(self, q):
        self.q = q
        self.total_count = None

    def query_index(self):
        return {
            "index": "scaife-viewer",
            "doc_type": "text",
        }

    def query(self):
        return {
            "simple_query_string": {
                "query": self.q,
                "fields": ["content"],
                "default_operator": "and",
            },
        }

    def search_kwargs(self, size=10, offset=0):
        return {
            "body": {
                "highlight": {
                    "fields": {
                        "content": {
                            "type": "fvh",
                        },
                    },
                },
                "query": self.query(),
                "aggs": {
                    "filtered_text_groups": {
                        "terms": {
                            "field": "text_group",
                        },
                    },
                },
            },
            "size": size,
            "from_": offset,
            **self.query_index()
        }

    def search_window(self, size, offset):
        return SearchResultSet(es.search(**self.search_kwargs(size, offset)))

    def count(self):
        if self.total_count is None:
            self.total_count = es.count(**{
                "body": {"query": self.query()},
                **self.query_index()
            })["count"]
        return self.total_count

    def __getitem__(self, key):
        if isinstance(key, slice):
            size = len(range(*key.indices(self.total_count)))
            return self.search_window(size, key.start)
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
            "link": reverse("reader", kwargs={"urn": link_urn}),
        }

    def filtered_text_groups(self):
        buckets = []
        for bucket in self.response["aggregations"]["filtered_text_groups"]["buckets"]:
            buckets.append({
                "text_group": cts.collection(bucket["key"]),
                "count": bucket["doc_count"],
            })
        return sorted(buckets, key=itemgetter("count"), reverse=True)
