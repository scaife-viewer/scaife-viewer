from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View

from . import cts
from .cts.utils import natural_keys as nk
from .reading.models import ReadingLog
from .search import SearchQuery, es
from .utils import apify, link_passage, encode_link_header


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


class LibraryView(BaseLibraryView):

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


class LibraryCollectionView(BaseLibraryView):

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


class LibraryCollectionVectorView(View):

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


class LibraryPassageView(View):

    def get(self, request, urn):
        try:
            passage = cts.passage(urn)
        except cts.PassageDoesNotExist:
            raise Http404()
        lo = {}
        prev, nxt = passage.prev(), passage.next()
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
        response = JsonResponse(apify(passage))
        if lo:
            response["Link"] = encode_link_header(lo)
        return response


def reader(request, urn):
    right_version = request.GET.get("right")
    try:
        passage = cts.passage(urn)
    except (cts.CollectionDoesNotExist, cts.PassageDoesNotExist):
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
