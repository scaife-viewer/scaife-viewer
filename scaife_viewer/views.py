import datetime
import json
import os
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView

import dateutil.parser
import requests

from . import cts
from .http import ConditionMixin
from .search import SearchQuery
from .utils import apify, encode_link_header, link_passage


def home(request):
    return render(request, "homepage.html", {})


def profile(request):
    return render(request, "profile.html", {})


class BaseLibraryView(View):

    format = "html"

    def get(self, request, **kwargs):
        to_response = {
            "html": self.as_html,
            "json": self.as_json,
        }.get(self.format, "html")
        return to_response()


class LibraryConditionMixin(ConditionMixin):

    def get_last_modified(self, request, *args, **kwargs):
        # @@@ per-URN modification dates will need nautilus-cnd
        # for now, use only deployment creation timestamp.
        last_modified = datetime.datetime.utcnow()
        deployment_timestamp = os.environ.get("EC_DEPLOYMENT_CREATED")
        if deployment_timestamp:
            last_modified = dateutil.parser.parse(deployment_timestamp)
        return last_modified


class LibraryView(LibraryConditionMixin, BaseLibraryView):

    def as_html(self):
        return render(self.request, "library/index.html", {})

    def as_json(self):
        all_text_groups = cts.text_inventory().text_groups()
        text_groups = []
        works = []
        texts = []
        for text_group in all_text_groups:
            for work in text_group.works():
                works.append(work)
                for text in work.texts():
                    texts.append(text)
            text_groups.append(text_group)
        payload = {
            "text_groups": [apify(text_group) for text_group in text_groups],
            "works": [apify(work) for work in works],
            "texts": [apify(text, with_toc=False) for text in texts],
        }
        return JsonResponse(payload)


class LibraryCollectionView(LibraryConditionMixin, BaseLibraryView):

    def validate_urn(self):
        if not self.kwargs["urn"].startswith("urn:"):
            raise Http404()

    def get_collection(self):
        self.validate_urn()
        return cts.collection(self.kwargs["urn"])

    def as_html(self):
        collection = self.get_collection()
        collection_name = collection.__class__.__name__.lower()
        ctx = {
            collection_name: collection,
        }
        return render(self.request, f"library/cts_{collection_name}.html", ctx)

    def as_json(self):
        collection = self.get_collection()
        return JsonResponse(apify(collection))


class LibraryCollectionVectorView(LibraryConditionMixin, View):

    def get(self, request, urn):
        entries = request.GET.getlist("e")
        collections = {}
        for entry in entries:
            collection = cts.collection(f"{urn}.{entry}")
            collections[str(collection.urn)] = apify(collection)
        payload = {
            "collections": collections,
        }
        return JsonResponse(payload)


class LibraryPassageView(LibraryConditionMixin, View):

    format = "json"

    def get(self, request, **kwargs):
        try:
            passage, healed = self.get_passage()
        except cts.InvalidPassageReference as e:
            return HttpResponse(
                json.dumps({
                    "reason": str(e),
                }),
                status=400,
                content_type="application/json",
            )
        if healed:
            key = {
                "json": "json_url",
                "text": "text_url",
            }.get(self.format, "json")
            redirect = HttpResponse(status=303)
            redirect["Location"] = link_passage(str(passage.urn))[key]
            return redirect
        self.passage = passage
        to_response = {
            "json": self.as_json,
            "text": self.as_text,
        }.get(self.format, "json")
        return to_response()

    def get_passage(self):
        urn = self.kwargs["urn"]
        try:
            return cts.passage_heal(urn)
        except cts.PassageDoesNotExist:
            raise Http404()

    def as_json(self):
        lo = {}
        prev, nxt = self.passage.prev(), self.passage.next()
        if prev:
            lo["prev"] = {
                "target": link_passage(str(prev.urn))["url"],
                "urn": str(prev.urn),
            }
        if nxt:
            lo["next"] = {
                "target": link_passage(str(nxt.urn))["url"],
                "urn": str(nxt.urn),
            }
        response = JsonResponse(apify(self.passage))
        if lo:
            response["Link"] = encode_link_header(lo)
        return response

    def as_text(self):
        return HttpResponse(
            f"{self.passage.content}\n",
            content_type="text/plain; charset=utf-8",
        )


class Reader(TemplateView):

    template_name = "reader/reader.html"

    def get_text(self):
        urn = cts.URN(self.kwargs["urn"])
        try:
            text = cts.collection(urn.upTo(cts.URN.NO_PASSAGE))
        except cts.CollectionDoesNotExist:
            raise Http404()
        return text

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["text"] = self.get_text()
        return context


def library_text_redirect(request, urn):
    """
    Given a text URN redirect to the first chunk. Required to prevent
    TOCing on the top-level library page.
    """
    try:
        text = cts.collection(urn)
    except cts.CollectionDoesNotExist:
        raise Http404()
    if not isinstance(text, cts.Text):
        raise Http404()
    passage = text.first_passage()
    if not passage:
        raise Http404()
    return redirect("reader", urn=passage.urn)


def search(request):
    q = request.GET.get("q", "")
    try:
        page_num = int(request.GET.get("p", 1))
    except ValueError:
        page_num = 1
    kind = request.GET.get("kind", "form")
    results = []
    ctx = {
        "q": q,
        "results": results,
        "kind": kind,
    }
    if q:
        scope = {}
        text_group_urn = request.GET.get("tg")
        if text_group_urn:
            scope["text_group"] = text_group_urn
        kwargs = {
            "scope": scope,
            "aggregate_field": "text_group",
            "kind": kind,
        }
        sq = SearchQuery(q, **kwargs)
        paginator = Paginator(sq, 10)
        ctx.update({
            "paginator": paginator,
            "page": paginator.page(page_num),
        })
    return render(request, "search.html", ctx)


def search_json(request):
    q = request.GET.get("q", "")
    size = int(request.GET.get("size", "10"))
    offset = int(request.GET.get("offset", "0"))
    pivot = request.GET.get("pivot")
    data = {"results": []}
    if q:
        scope = {}
        text_group_urn = request.GET.get("text_group")
        work_urn = request.GET.get("work")
        text_urn = request.GET.get("text")
        passage_urn = request.GET.get("passage")
        if text_group_urn:
            scope["text_group"] = text_group_urn
        elif work_urn:
            scope["work"] = work_urn
        elif text_urn:
            scope["text.urn"] = text_urn
        elif passage_urn:
            scope["urn"] = passage_urn
        query_kwargs = {
            "scope": scope,
            "sort_by": "document",
            "kind": request.GET.get("kind", "form"),
        }
        sq = SearchQuery(q, **query_kwargs)
        if "text.urn" in scope and pivot:
            urn = cts.URN(pivot)
            urn_start = f"{urn.upTo(cts.URN.NO_PASSAGE)}:{urn.reference.start}"
            for doc_offset, doc in enumerate(sq.scan()):
                if doc["_id"] == urn_start:
                    start_offset = max(0, doc_offset - (size // 2))
                    data["pivot"] = {
                        "offset": doc_offset,
                        "start_offset": start_offset,
                        "end_offset": start_offset + size - 1,
                    }
                    offset = start_offset
                    break
        data["total_count"] = sq.count()
        fields = set(request.GET.get("fields", "content,highlights").split(","))
        for result in sq.search_window(size=size, offset=offset):
            r = {
                "passage": apify(result["passage"], with_content=False),
            }
            if "content" in fields:
                r["content"] = result["content"]
            if "highlights" in fields:
                r["highlights"] = [
                    dict(w=w, i=i)
                    for w, i in result["highlights"]
                ]
            data["results"].append(r)
    return JsonResponse(data)


def morpheus(request):
    if ("word" not in request.GET) or ("lang" not in request.GET):
        return HttpResponseBadRequest(
            content='Error when processing morpheus request: "word" and "lang" parameters are required'
        )
    word = request.GET["word"]
    lang = request.GET["lang"]
    allowed_langs = ["grc", "lat"]
    if lang not in allowed_langs:
        return HttpResponseBadRequest(
            content='Error when processing morpheus request: "lang" parameter must be one of: {}'.format(", ".join(allowed_langs))
        )
    params = {
        "word": word,
        "lang": lang,
        "engine": f"morpheus{lang}",
    }
    qs = urlencode(params)
    url = f"http://services.perseids.org/bsp/morphologyservice/analysis/word?{qs}"
    headers = {
        "Accept": "application/json",
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    body = r.json().get("RDF", {}).get("Annotation", {}).get("Body", [])
    if not isinstance(body, list):
        body = [body]
    data_body = []
    for item in body:
        entry = {
            "uri": item["rest"]["entry"]["uri"],
            # "dict": item["rest"]["entry"]["dict"],
            "hdwd": item["rest"]["entry"]["dict"]["hdwd"]["$"],
            "pofs": item["rest"]["entry"]["dict"]["pofs"]["$"],
        }
        if "decl" in item["rest"]["entry"]["dict"]:
            entry["decl"] = item["rest"]["entry"]["dict"]["decl"]["$"]
        infl_body = item["rest"]["entry"]["infl"]
        if not isinstance(infl_body, list):
            infl_body = [infl_body]
        infl_list = []
        for infl_item in infl_body:
            infl_entry = {
                # "raw": infl_item,
            }
            infl_entry["stem"] = infl_item["term"]["stem"]["$"]
            if "suff" in infl_item["term"]:
                infl_entry["suff"] = infl_item["term"]["suff"].get("$", "")
            infl_entry["pofs"] = infl_item["pofs"]["$"]
            if "case" in infl_item:
                infl_entry["case"] = infl_item["case"]["$"]
            if "mood" in infl_item:
                infl_entry["mood"] = infl_item["mood"]["$"]
            if "tense" in infl_item:
                infl_entry["tense"] = infl_item["tense"]["$"]
            if "voice" in infl_item:
                infl_entry["voice"] = infl_item["voice"]["$"]
            if "gend" in infl_item:
                infl_entry["gend"] = infl_item["gend"]["$"]
            if "num" in infl_item:
                infl_entry["num"] = infl_item["num"]["$"]
            if "pers" in infl_item:
                infl_entry["pers"] = infl_item["pers"]["$"]
            if "comp" in infl_item:
                infl_entry["comp"] = infl_item["comp"]["$"]
            if "dial" in infl_item:
                infl_entry["dial"] = infl_item["dial"]["$"]
            infl_entry["stemtype"] = infl_item["stemtype"]["$"]
            if "derivtype" in infl_item:
                infl_entry["derivtype"] = infl_item["derivtype"]["$"]
            if "morph" in infl_item:
                infl_entry["morph"] = infl_item["morph"]["$"]
            infl_list.append(infl_entry)
        entry["infl"] = infl_list
        data_body.append(entry)
    data = {"Body": data_body}
    return JsonResponse(data)
