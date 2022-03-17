from django.db.models import Count
from django.shortcuts import render

from scaife_viewer.atlas.models import Repo

from .stats import get_library_stats


def home(request):
    return render(request, "homepage.html", {"stats": get_library_stats()})


def about(request):
    repos = Repo.objects.annotate(version_count=Count("urns")).order_by(
        "-version_count"
    )
    return render(request, "about.html", {"repos": repos})


def profile(request):
    return render(request, "profile.html", {})


def app(request, *args, **kwargs):
    return render(request, "app.html", {})
