import datetime
import json
import os
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse
)
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


def about(request):
    return render(request, "about.html", {})


def profile(request):
    return render(request, "profile.html", {})


def app(request, *args, **kwargs):
    return render(request, "app.html", {})


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
        try:
            return cts.collection(self.kwargs["urn"])
        except cts.CollectionDoesNotExist:
            raise Http404()

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
        try:
            cts.collection(urn)
        except cts.CollectionDoesNotExist:
            raise Http404()
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
    return render(request, "search.html", {})


def search_text(request):
    dummy_results = [{"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.1", "refs": {"start": {"reference": "1.1", "human_reference": "Book 1 Chapter 1"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.2", "refs": {"start": {"reference": "1.2", "human_reference": "Book 1 Chapter 2"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.3", "refs": {"start": {"reference": "1.3", "human_reference": "Book 1 Chapter 3"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.4", "refs": {"start": {"reference": "1.4", "human_reference": "Book 1 Chapter 4"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.5", "refs": {"start": {"reference": "1.5", "human_reference": "Book 1 Chapter 5"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.6", "refs": {"start": {"reference": "1.6", "human_reference": "Book 1 Chapter 6"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.7/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.7/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.7", "refs": {"start": {"reference": "1.7", "human_reference": "Book 1 Chapter 7"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.8/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.8/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.8", "refs": {"start": {"reference": "1.8", "human_reference": "Book 1 Chapter 8"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.9/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.9/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.9", "refs": {"start": {"reference": "1.9", "human_reference": "Book 1 Chapter 9"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.10/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.10/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:1.10", "refs": {"start": {"reference": "1.10", "human_reference": "Book 1 Chapter 10"}}, "ancestors": [{"reference": "1"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.1", "refs": {"start": {"reference": "2.1", "human_reference": "Book 2 Chapter 1"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.2", "refs": {"start": {"reference": "2.2", "human_reference": "Book 2 Chapter 2"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.3", "refs": {"start": {"reference": "2.3", "human_reference": "Book 2 Chapter 3"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.4", "refs": {"start": {"reference": "2.4", "human_reference": "Book 2 Chapter 4"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.5", "refs": {"start": {"reference": "2.5", "human_reference": "Book 2 Chapter 5"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.6", "refs": {"start": {"reference": "2.6", "human_reference": "Book 2 Chapter 6"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.7/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.7/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:2.7", "refs": {"start": {"reference": "2.7", "human_reference": "Book 2 Chapter 7"}}, "ancestors": [{"reference": "2"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.1", "refs": {"start": {"reference": "3.1", "human_reference": "Book 3 Chapter 1"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.2", "refs": {"start": {"reference": "3.2", "human_reference": "Book 3 Chapter 2"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.3", "refs": {"start": {"reference": "3.3", "human_reference": "Book 3 Chapter 3"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.4", "refs": {"start": {"reference": "3.4", "human_reference": "Book 3 Chapter 4"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.5", "refs": {"start": {"reference": "3.5", "human_reference": "Book 3 Chapter 5"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.6", "refs": {"start": {"reference": "3.6", "human_reference": "Book 3 Chapter 6"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7", "refs": {"start": {"reference": "3.7", "human_reference": "Book 3 Chapter 7"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.8/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.8/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.8", "refs": {"start": {"reference": "3.8", "human_reference": "Book 3 Chapter 8"}}, "ancestors": [{"reference": "3"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.1", "refs": {"start": {"reference": "4.1", "human_reference": "Book 4 Chapter 1"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.2", "refs": {"start": {"reference": "4.2", "human_reference": "Book 4 Chapter 2"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.3", "refs": {"start": {"reference": "4.3", "human_reference": "Book 4 Chapter 3"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.4", "refs": {"start": {"reference": "4.4", "human_reference": "Book 4 Chapter 4"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.5", "refs": {"start": {"reference": "4.5", "human_reference": "Book 4 Chapter 5"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.6", "refs": {"start": {"reference": "4.6", "human_reference": "Book 4 Chapter 6"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.7/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.7/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:4.7", "refs": {"start": {"reference": "4.7", "human_reference": "Book 4 Chapter 7"}}, "ancestors": [{"reference": "4"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.1", "refs": {"start": {"reference": "5.1", "human_reference": "Book 5 Chapter 1"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.2", "refs": {"start": {"reference": "5.2", "human_reference": "Book 5 Chapter 2"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.3", "refs": {"start": {"reference": "5.3", "human_reference": "Book 5 Chapter 3"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.4", "refs": {"start": {"reference": "5.4", "human_reference": "Book 5 Chapter 4"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.5", "refs": {"start": {"reference": "5.5", "human_reference": "Book 5 Chapter 5"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:5.6", "refs": {"start": {"reference": "5.6", "human_reference": "Book 5 Chapter 6"}}, "ancestors": [{"reference": "5"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.1/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.1/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.1", "refs": {"start": {"reference": "6.1", "human_reference": "Book 6 Chapter 1"}}, "ancestors": [{"reference": "6"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.2/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.2/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.2", "refs": {"start": {"reference": "6.2", "human_reference": "Book 6 Chapter 2"}}, "ancestors": [{"reference": "6"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.3/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.3/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.3", "refs": {"start": {"reference": "6.3", "human_reference": "Book 6 Chapter 3"}}, "ancestors": [{"reference": "6"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.4/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.4/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.4", "refs": {"start": {"reference": "6.4", "human_reference": "Book 6 Chapter 4"}}, "ancestors": [{"reference": "6"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.5/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.5/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.5", "refs": {"start": {"reference": "6.5", "human_reference": "Book 6 Chapter 5"}}, "ancestors": [{"reference": "6"}], "children": []}}, {"passage": {"url": "/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.6/", "json_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.6/json/", "text": {"url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/", "ancestors": [{"url": "/library/urn:cts:pdlpsci:bodin/", "json_url": "/library/urn:cts:pdlpsci:bodin/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin/text/", "urn": "urn:cts:pdlpsci:bodin", "label": "Bodin"}, {"url": "/library/urn:cts:pdlpsci:bodin.livrep/", "json_url": "/library/urn:cts:pdlpsci:bodin.livrep/json/", "text_url": "/library/passage/urn:cts:pdlpsci:bodin.livrep/text/", "urn": "urn:cts:pdlpsci:bodin.livrep", "label": "The Six Books of a Commonweale"}], "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1", "label": "1606 The Six Books of a Commonweale", "lang": "eng", "human_lang": "English", "kind": "translation"}, "urn": "urn:cts:pdlpsci:bodin.livrep.perseus-eng1:6.6", "refs": {"start": {"reference": "6.6", "human_reference": "Book 6 Chapter 6"}}, "ancestors": [{"reference": "6"}], "children": []}}]

    q = request.GET.get("q", "")
    page_num = int(request.GET.get("page_num"))
    start_index = int(request.GET.get("start_index"))
    end_index = int(request.GET.get("end_index"))
    data = {
        "q": q,
        "page_num": page_num,
        "start_index": start_index,
        "end_index": end_index
    }
    if q:
        start_index = page_num
        end_index = page_num + 10
        results = dummy_results[start_index:end_index]
        data["results"] = results
        import math
        data["total_pages"] =  math.ceil(len(dummy_results) / 10)
        data["total_results"] =  len(dummy_results)
    print(data)
    return JsonResponse(data)


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
