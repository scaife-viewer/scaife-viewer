from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render

from scaife_viewer.atlas.models import Repo

from .changelog.keyfile import cachekeys
from .changelog.models import ChangelogEntry
from .stats import get_library_stats


CACHE_FOREVER = None
LATEST_CHANGELOG_KEY = cachekeys["LATEST_CHANGELOG"]


def home(request):
    changelog = cache.get(LATEST_CHANGELOG_KEY, None)
    if not changelog:
        changelog = ChangelogEntry.objects.order_by("-timestamp")[0:3]
        cache.set(LATEST_CHANGELOG_KEY, changelog, CACHE_FOREVER)
    return render(
        request,
        "homepage.html",
        {
            "stats": get_library_stats(),
            "changelog": changelog,
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
