from http import HTTPStatus

from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.vary import vary_on_headers

import mimeparse

from .cts import CTS
from .reading.models import ReadingLog


def home(request):
    return render(request, "homepage.html", {})


def profile(request):
    return render(request, "profile.html", {})


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
        "label": work.resource.get_label(lang="eng"),
        "url": reverse("library_cts_resource", kwargs={"urn": work.resource.urn}),
        "texts": [
            serialize_text(text)
            for text in work.texts()
        ]
    }


def serialize_text(text):
    return {
        "label": text.resource.get_label(lang="eng"),
        "description": text.resource.get_description(lang="eng"),
        "subtype": text.resource.SUBTYPE,
        "lang": text.resource.lang,
        "human_lang": text.human_lang,
        "browse_url": reverse("library_cts_resource", kwargs={"urn": text.resource.urn}),
        "read_url": reverse("reader", kwargs={"urn": text.resource.urn}),
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
        if resource.kind == "text":
            toc = cts.passage(urn).toc()
            obj = [
                {
                    "label": ref_node.label.title(),
                    "num": ref_node.num,
                    "reader_url": reverse("reader", kwargs={"urn": next(toc.chunks(ref_node), None).urn}),
                }
                for ref_node in toc.num_resolver.glob(toc.root, "*")
            ]
        return JsonResponse({"object": obj})
    if content_type == "text/html":
        ctx = {
            resource.kind: resource,
            "parents": list(reversed(resource.resource.parents))[1:]
        }
        return render(request, f"library/cts_{resource.kind}.html", ctx)
    return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)


def reader(request, urn):
    cts = CTS()
    passage = cts.passage(urn)
    if cts.is_resource(urn):
        return redirect("reader", urn=passage.first_urn)
    ctx = {
        "passage": passage,
        "parents": list(reversed(passage.metadata.parents))[1:]
    }
    response = render(request, "reader/reader.html", ctx)
    if request.user.is_authenticated():
        ReadingLog.objects.create(user=request.user, urn=urn)
    return response


def healthz(request):
    return HttpResponse(content="ok")
