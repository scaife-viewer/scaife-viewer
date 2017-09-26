from django.shortcuts import render, redirect

from .cts import CTS


def home(request):
    cts = CTS()
    ctx = {
        "resources": cts.resources(),
    }
    return render(request, "homepage.html", ctx)


def cts_resource(request, urn):
    cts = CTS()
    if not cts.is_resource(urn):
        raise Exception("not resource")
    resource = cts.resource(urn)
    ctx = {
        resource.kind: resource,
        "parents": list(reversed(resource.resource.parents))[1:]
    }
    return render(request, f"cts_{resource.kind}.html", ctx)


def reader(request, urn):
    cts = CTS()
    if cts.is_resource(urn):
        return redirect("reader", urn=cts.first_urn(urn))
    passage = cts.passage(urn)
    ctx = {
        "passage": passage,
    }
    return render(request, "reader.html", ctx)
