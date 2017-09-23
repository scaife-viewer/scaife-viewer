from django.shortcuts import render, redirect

from lxml import etree
from MyCapytain.common.reference import URN
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


def home(request):

    urn = request.GET.get("urn")
    if urn:
        urn = URN(urn)

    # The follow code is a super simple way of traversing a CTS API.
    # This is effectively the same as resolver.getMetadata, but tweaked very slightly
    # to allow displaying a the collection of text groups.
    retriever = HttpCtsRetriever("https://perseus-cts.us1.eldarioncloud.com/api/cts")
    ti = XmlCtsTextInventoryMetadata.parse(retriever.getCapabilities(urn=str(urn)))
    if urn:
        ti = [x for x in [ti] + ti.descendants if x.id == str(urn)][0]
    resources = []
    for o in ti.members:
        resource = {
            "urn": o.id,
            "label": o.get_label(lang="eng"),
            "readable": o.readable,
        }
        resources.append(resource)

    ctx = {
        "resources": resources,
    }

    return render(request, "homepage.html", ctx)


def reader(request):

    urn = URN(request.GET["urn"])
    version_urn = urn.upTo(URN.VERSION)

    retriever = HttpCtsRetriever("https://perseus-cts.us1.eldarioncloud.com/api/cts")
    resolver = HttpCtsResolver(retriever)
    reffs = resolver.getReffs(urn)
    if len(reffs):
        return redirect("/reader" + f"?urn={version_urn}:{reffs[0]}")
    node = resolver.getTextualNode(urn)
    tei = node.resource
    with open("tei.xsl") as f:
        transform = etree.XSLT(etree.XML(f.read()))
    text = transform(tei)

    next_urn = f"{version_urn}:{node.nextId}" if node.nextId else None
    prev_urn = f"{version_urn}:{node.prevId}" if node.prevId else None

    ctx = {
        "text": text,
        "next": next_urn,
        "prev": prev_urn,
        "ancestors": [],  # @@@
        "children": [],  # @@@
    }

    return render(request, "reader.html", ctx)
