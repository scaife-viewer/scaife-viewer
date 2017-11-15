from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

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
            },
            "size": size,
            "from_": offset,
            **self.query_index()
        }

    def search_window(self, size, offset):
        response = es.search(**self.search_kwargs(size, offset))
        for hit in response["hits"]["hits"]:
            yield self.result(hit)

    def result(self, hit):
        passage = cts.passage(hit["_id"])
        link_urn = passage.urn  # @@@ consider dynamically chunking and giving a better passage URN
        return {
            "passage": passage,
            "content": mark_safe("\n".join(f"<p>{c}</p>" for c in hit["highlight"]["content"])),
            "link": reverse("reader", kwargs={"urn": link_urn}),
        }

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
            return list(self.search_window(size, key.start))
        raise NotImplementedError()
