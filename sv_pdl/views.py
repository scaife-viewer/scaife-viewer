from typing import Any
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

import requests
from github import Github
from scaife_viewer.atlas.models import Repo
from scaife_viewer.core import cts
from scaife_viewer.core.utils import apify, get_pagination_info

from .changelog.keyfile import cachekeys
from .search import SearchQuery
from .stats import get_library_stats


CACHE_FOREVER = None
LATEST_RELEASE_KEY = cachekeys["LATEST_RELEASE"]


def _latest_release():
    try:
        client = Github()
        repo = client.get_repo("scaife-viewer/scaife-viewer")
        release = release = next(iter(repo.get_releases()))
        return {"title": release.title, "url": release.html_url}
    except Exception:
        return {}


def home(request):
    release = cache.get(LATEST_RELEASE_KEY, None)
    if not release:
        release = _latest_release()
        cache.set(LATEST_RELEASE_KEY, release, CACHE_FOREVER)
    return render(
        request,
        "homepage.html",
        {
            "stats": get_library_stats(),
            "release": release,
        },
    )


def about(request):
    repos = Repo.objects.annotate(version_count=Count("urns")).order_by(
        "-version_count"
    )
    return render(request, "about.html", {"repos": repos})


def commentaries(request, *args, **kwargs):
    page = request.GET.get("page", 1)
    url = f"{settings.SV_NEW_ATLAS_API_URL}/commentaries/passage/{kwargs['urn']}/?page={page}"

    response = requests.get(url)

    if response.status_code == 200:
        return JsonResponse(response.json())

    return JsonResponse({})


def dictionary_entries(request, *args, **kwargs):
    page = request.GET.get("page", 1)
    url = f"{settings.SV_NEW_ATLAS_API_URL}/dictionaries/{kwargs['slug']}/entries/?page={page}"

    q = request.GET.get("q", None)

    if q is not None:
        url = f"{url}&q={q}"

    response = requests.get(url)

    if response.status_code == 200:
        return JsonResponse(response.json())

    return JsonResponse([])


def dictionaries(request):
    response = requests.get(
        f"{settings.SV_NEW_ATLAS_API_URL}/dictionaries/json/",
        headers={"accept": "application/json"},
    )

    return JsonResponse(response.json())


def search_json(request):
    # get params from query string
    search_type = request.GET.get("type")
    q = request.GET.get("q", "")
    kind = request.GET.get("kind", "form")
    size = int(request.GET.get("size", "10"))
    text_group_urn = request.GET.get("text_group")
    work_urn = request.GET.get("work")

    # validate params
    if not search_type:
        return JsonResponse(
            {"error": "Provide a search type - 'library' or 'reader'."}, status=400
        )
    if not q:
        return JsonResponse({"error": "Provide a search query."}, status=400)

    scope = {}
    data: dict[str, Any] = {"results": []}

    # conduct search
    if search_type == "library":

        page_num = int(request.GET.get("page_num", "1"))
        aggregate_fields = {
            "filtered_text_group": {"terms": {"field": "text_group", "size": 300}}
        }

        data.update({"q": q, "kind": kind, "page_num": page_num, "type": search_type})

        if text_group_urn:
            scope["text_group"] = text_group_urn
            aggregate_fields["filtered_work"] = {
                "terms": {"field": "work", "size": 300}
            }

        if work_urn:
            scope = {}
            scope["work"] = work_urn

        kwargs = {
            "search_type": search_type,
            "scope": scope,
            "aggregate_fields": aggregate_fields,
            "kind": kind,
            "offset": (page_num - 1) * 10,
        }
        try:
            sq = SearchQuery(q, **kwargs)
        except Exception:
            return JsonResponse({"error": "Something went wrong."}, status=500)
        total_count = sq.count()
        page = get_pagination_info(total_count, page_num)
        results = sq.search_window(size=size, offset=((page_num - 1) * 10))

        for result in results:
            r = {"passage": apify(result["passage"], with_content=False)}
            if kind == "form":
                r["content"] = result["raw_content"]
            else:
                r["content"] = result["content"]
            data["results"].append(r)

        data.update(
            {
                "text_groups": results.filtered_aggs("filtered_text_group"),
                "works": results.filtered_aggs("filtered_work")
                if text_group_urn
                else None,
                "total_count": total_count,
                "page": page,
            }
        )

    else:

        offset = int(request.GET.get("offset", "0"))
        pivot = request.GET.get("pivot")
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
            "search_type": search_type,
            "scope": scope,
            "sort_by": "document",
            "kind": kind,
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
            r = {"passage": apify(result["passage"], with_content=False)}
            if "content" in fields:
                r["content"] = result["content"]
            if "highlights" in fields:
                r["highlights"] = [dict(w=w, i=i) for w, i in result["highlights"]]
            data["results"].append(r)

    return JsonResponse(data)


def profile(request):
    return render(request, "profile.html", {})


def app(request, *args, **kwargs):
    return render(request, "app.html", {})
