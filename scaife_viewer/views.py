from http import HTTPStatus

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.vary import vary_on_headers

import mimeparse

from . import cts
from .cts.utils import natural_keys as nk
from .reading.models import ReadingLog
from .search import SearchQuery


def home(request):
    return render(request, "homepage.html", {})


def profile(request):
    return render(request, "profile.html", {})


@vary_on_headers("Accept")
def library(request):
    content_type = mimeparse.best_match(["application/json", "text/html"], request.META["HTTP_ACCEPT"])
    if content_type == "application/json":
        text_groups = cts.text_inventory().text_groups()
        return JsonResponse({
            "object": [
                {
                    "label": text_group.label,
                    "url": reverse("library_cts_resource", kwargs={"urn": text_group.urn})
                }
                for text_group in text_groups
            ]
        })
    if content_type == "text/html":
        ctx = {}
        return render(request, "library/index.html", ctx)


def serialize_work(work):
    return {
        "label": work.label,
        "url": reverse("library_cts_resource", kwargs={"urn": work.urn}),
        "texts": [
            serialize_text(text)
            for text in work.texts()
        ]
    }


def serialize_text(text):
    return {
        "label": text.label,
        "description": text.description,
        "subtype": text.kind,
        "lang": text.lang,
        "human_lang": text.human_lang,
        "browse_url": reverse("library_cts_resource", kwargs={"urn": text.urn}),
        "read_url": reverse("reader", kwargs={"urn": text.first_passage().urn}),
    }


@vary_on_headers("Accept")
def library_cts_resource(request, urn):
    collection = cts.collection(urn)
    content_type = mimeparse.best_match(["application/json", "text/html"], request.META["HTTP_ACCEPT"])
    collection_name = collection.__class__.__name__.lower()
    if content_type == "application/json":
        if isinstance(collection, cts.TextGroup):
            works = []
            for work in collection.works():
                works.append(serialize_work(work))
            obj = works
        if isinstance(collection, cts.Work):
            texts = []
            for text in collection.texts():
                texts.append(serialize_text(text))
            obj = texts
        if isinstance(collection, cts.Text):
            toc = collection.toc()
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
            collection_name: collection,
        }
        return render(request, f"library/cts_{collection_name}.html", ctx)
    return HttpResponse(status=HTTPStatus.NOT_ACCEPTABLE)


def reader(request, urn):
    right_version = request.GET.get("right")
    try:
        passage = cts.passage(urn)
    except cts.PassageDoesNotExist:
        raise Http404()
    ctx = {
        "passage": passage,
    }
    image_collection_link_urns = {
        "urn:cts:greekLit:tlg0553.tlg001.1st1K-grc1": "https://digital.slub-dresden.de/id403855756",
    }
    if str(passage.urn) in image_collection_link_urns:
        ctx["image_collection_link"] = image_collection_link_urns[str(passage.urn)]
    passage_urn_to_image = {
        "urn:cts:greekLit:tlg0553.tlg001.1st1K-grc1": [
            (nk("1.18"), nk("1.21"), "https://digital.slub-dresden.de/data/goobi/403855756/403855756_tif/jpegs/00000033.tif.large.jpg"),
            (nk("1.21"), nk("1.21"), "https://digital.slub-dresden.de/data/goobi/403855756/403855756_tif/jpegs/00000034.tif.large.jpg"),
            (nk("1.22"), nk("1.22"), "https://digital.slub-dresden.de/data/goobi/403855756/403855756_tif/jpegs/00000035.tif.large.jpg"),
            (nk("1.22"), nk("1.24"), "https://digital.slub-dresden.de/data/goobi/403855756/403855756_tif/jpegs/00000036.tif.large.jpg"),
        ]
    }
    images = []
    if str(passage.urn.upTo(cts.URN.WORK)) in passage_urn_to_image:
        passage_start = passage.refs["start"].sort_key()
        passage_end = passage.refs.get("end", passage.refs["start"]).sort_key()
        for (start, end, image) in passage_urn_to_image[passage.urn]:
            if start < passage_start and end >= passage_start:
                if image not in images:
                    images.append(image)
            if start >= passage_start and start <= passage_end:
                if image not in images:
                    images.append(image)
    ctx["images"] = images
    if right_version:
        right_urn = f"{passage.text.urn.upTo(cts.URN.WORK)}.{right_version}:{passage.reference}"
        try:
            right_passage = cts.passage(right_urn)
        except cts.PassageDoesNotExist as e:
            right_text = e.text
            right_passage = None
            ctx["reader_error"] = mark_safe(f"Unable to load passage: <b>{right_urn}</b> was not found.")
        else:
            right_text = right_passage.text
            ctx.update({
                "right_version": right_version,
                "right_passage": right_passage,
            })
    versions = []
    for version in passage.text.versions():
        versions.append({
            "text": version,
            "left": (version.urn == passage.text.urn) if right_version else False,
            "right": (version.urn == right_text.urn) if right_version else False,
            "overall": version.urn == passage.text.urn and not right_version,
        })
    ctx["versions"] = versions
    response = render(request, "reader/reader.html", ctx)
    if request.user.is_authenticated():
        ReadingLog.objects.create(user=request.user, urn=urn)
        if right_version and right_passage:
            ReadingLog.objects.create(user=request.user, urn=right_urn)
    return response


def search(request):
    q = request.GET.get("q", "")
    try:
        page_num = int(request.GET.get("p", 1))
    except ValueError:
        page_num = 1
    results = []
    ctx = {
        "q": q,
        "results": results,
    }
    if q:
        paginator = Paginator(SearchQuery(q), 10)
        ctx.update({
            "paginator": paginator,
            "page": paginator.page(page_num),
        })
    return render(request, "search.html", ctx)
