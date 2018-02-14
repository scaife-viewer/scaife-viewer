from collections import defaultdict
from itertools import tee
from operator import itemgetter

from django.conf import settings
from django.core.urlresolvers import reverse

import regex
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as scanner

from . import cts

es = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])


class SearchQuery:

    def __init__(self, q, scope=None, sort_by=None, aggregate_field=None, kind="form"):
        self.q = q
        self.scope = {} if scope is None else scope
        self.sort_by = sort_by
        self.aggregate_field = aggregate_field
        self.kind = kind
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
        if self.kind == "lemma":
            fields = ["lemma_content"]
        else:
            fields = ["content"]
        sq = {
            "simple_query_string": {
                "query": self.q,
                "fields": fields,
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

    def query_highlight(self):
        if self.kind == "lemma":
            fields = {"lemma_content": {}}
        else:
            fields = {"content": {}}
        return {
            "highlight": {
                "type": "fvh",
                "number_of_fragments": 0,
                "fields": fields,
            }
        }

    def search_kwargs(self, size=10, offset=0):
        return {
            "body": {
                **self.query_sort(),
                **self.query_highlight(),
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
        highlighter = Highlighter(
            passage,
            hit["highlight"].get("content", [""])[0],
            hit["highlight"].get("lemma_content", [""])[0],
        )
        return {
            "passage": passage,
            "content": highlighter.fragments(),
            "highlights": highlighter.tokens(),
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


w = fr"(?:<em>)?(?:\w[-\w]*|{chr(0xfffd)})(?:</em>)?"
p = r"\p{P}+"
token_re = regex.compile(fr"{w}|{p}")  # no ws needed to align with lemmas
w_re = regex.compile(w)


class Highlighter:

    def __init__(self, passage, *highlights):
        self.passage = passage
        self.highlights = highlights

    def tokens(self):
        if not hasattr(self, "_tokens"):
            acc = set()
            idx = defaultdict(int)
            sit = iter(
                tee(
                    iter([t["w"] for t in self.passage.tokenize(whitespace=False)]),
                    len(self.highlights)
                )
            )
            for content in self.highlights:
                it = zip(token_re.findall(content), next(sit))
                for hw, sw in it:
                    if hw:
                        wl = len(sw)
                        highlighted = False
                        if w_re.match(hw):
                            highlighted = "<em>" in hw
                        for wk in (sw[i:j + 1] for i in range(wl) for j in range(i, wl)):
                            idx[wk] += 1
                        if highlighted:
                            acc.add((sw, idx[sw]))
            self._tokens = acc
        return self._tokens

    def content(self):
        if not hasattr(self, "_tokens"):
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
