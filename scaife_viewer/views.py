import mimeparse

from http import HTTPStatus

from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .cts import CTS


def home(request):
    cts = CTS()
    content_type = mimeparse.best_match(["application/json", "text/html"], request.META["HTTP_ACCEPT"])
    if content_type == "application/json":
        resources = cts.resources()
        return JsonResponse({
            "object": [
                {
                    "label": r.label,
                    "url": reverse("cts_resource", kwargs={"urn": r.urn})
                }
                for r in resources
            ]
        })
    if content_type == "text/html":
        ctx = {}
        return render(request, "homepage.html", ctx)


def serialize_work(work):
    return {
        "label": work.get_label(lang="eng"),
        "url": reverse("cts_resource", kwargs={"urn": work.urn}),
        "texts": [
            serialize_text(text)
            for text in work.texts.values()
        ]
    }


def serialize_text(text):
    return {
        "label": text.get_label(lang="eng"),
        "description": text.get_description(lang="eng"),
        "url": reverse("reader", kwargs={"urn": text.urn}),
    }


def cts_resource(request, urn):
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
        return render(request, f"cts_{resource.kind}.html", ctx)
    return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)


def reader(request, urn):
    cts = CTS()
    if cts.is_resource(urn):
        return redirect("reader", urn=cts.first_urn(urn))
    passage = cts.passage(urn)
    ctx = {
        "passage": passage,
        "parents": list(reversed(passage.metadata.parents))[1:]
    }
    return render(request, "reader.html", ctx)
