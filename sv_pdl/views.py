from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render

from github import Github
from scaife_viewer.atlas.models import Repo

from .changelog.keyfile import cachekeys
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


def profile(request):
    return render(request, "profile.html", {})


def app(request, *args, **kwargs):
    return render(request, "app.html", {})
