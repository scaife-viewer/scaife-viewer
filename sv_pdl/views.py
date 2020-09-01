from django.shortcuts import render

from .stats import get_library_stats


def home(request):
    return render(request, "homepage.html", {"stats": get_library_stats()})


def about(request):
    return render(request, "about.html", {})


def profile(request):
    return render(request, "profile.html", {})


def app(request, *args, **kwargs):
    return render(request, "app.html", {})
