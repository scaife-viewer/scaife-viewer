import mimeparse

from http import HTTPStatus

from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.vary import vary_on_headers

from .cts import CTS


def home(request):
    return render(request, "homepage.html", {})


@vary_on_headers("Accept")
def library(request):
    cts = CTS()
    content_type = mimeparse.best_match(["application/json", "text/html"], request.META["HTTP_ACCEPT"])
    if content_type == "application/json":
        resources = cts.resources()
        return JsonResponse({
            "object": [
                {
                    "label": r.label,
                    "url": reverse("library_cts_resource", kwargs={"urn": r.urn})
                }
                for r in resources
            ]
        })
    if content_type == "text/html":
        ctx = {}
        return render(request, "library/index.html", ctx)


def serialize_work(work):
    return {
        "label": work.get_label(lang="eng"),
        "url": reverse("library_cts_resource", kwargs={"urn": work.urn}),
        "texts": [
            serialize_text(text)
            for text in work.texts.values()
        ]
    }


def serialize_text(text):
    return {
        "label": text.get_label(lang="eng"),
        "description": text.get_description(lang="eng"),
        "subtype": text.SUBTYPE,
        "lang": text.lang,
        "url": reverse("library_reader", kwargs={"urn": text.urn}),
    }


@vary_on_headers("Accept")
def library_cts_resource(request, urn):
    cts = CTS()
    if not cts.is_resource(urn):
        raise Exception("not resource")
    resource = cts.resource(urn)
    content_type = mimeparse.best_match(["application/json", "text/html"], request.META["HTTP_ACCEPT"])
    if content_type == "application/json":
        if resource.kind == "textgroup":
            works = []
            for work in resource.works():
                works.append(serialize_work(work))
            obj = works
        if resource.kind == "work":
            texts = []
            for text in resource.texts():
                texts.append(serialize_text(text))
            obj = texts
        return JsonResponse({"object": obj})
    if content_type == "text/html":
        ctx = {
            resource.kind: resource,
            "parents": list(reversed(resource.resource.parents))[1:]
        }
        return render(request, f"library/cts_{resource.kind}.html", ctx)
    return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)


def library_reader(request, urn):
    cts = CTS()
    if cts.is_resource(urn):
        return redirect("library_reader", urn=cts.first_urn(urn))
    passage = cts.passage(urn)
    ctx = {
        "passage": passage,
        "parents": list(reversed(passage.metadata.parents))[1:]
    }
    return render(request, "library/reader.html", ctx)
