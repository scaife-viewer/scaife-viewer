from django.core.urlresolvers import reverse

from . import cts


def link_collection(urn) -> dict:
    return {
        "url": reverse("library_collection", kwargs={"urn": urn}),
        "json_url": reverse("library_collection_json", kwargs={"urn": urn})
    }


def link_passage(urn) -> dict:
    return {
        "url": reverse("reader", kwargs={"urn": urn}),
        "json_url": reverse("library_passage_json", kwargs={"urn": urn}),
    }


def apify(obj, **kwargs):
    remaining = obj.as_json(**kwargs)
    rels = {}
    if isinstance(obj, cts.TextGroup):
        works = remaining.pop("works")
        rels = {
            "works": [
                {
                    **link_collection(work["urn"]),
                    **work,
                    "texts": [
                        {
                            **link_collection(text["urn"]),
                            "reader_url": reverse("library_text_redirect", kwargs={"urn": text["urn"]}),
                            **text
                        }
                        for text in work["texts"]
                    ],
                }
                for work in works
            ],
        }
    if isinstance(obj, cts.Work):
        texts = remaining.pop("texts")
        rels = {
            "texts": [{**link_collection(text["urn"]), **text} for text in texts],
        }
    if isinstance(obj, cts.Text):
        first_passage = remaining.pop("first_passage")
        ancestors = remaining.pop("ancestors")
        toc = remaining.pop("toc")
        rels = {
            "first_passage": {**link_passage(first_passage["urn"]), **first_passage},
            "ancestors": [{**link_collection(ancestor["urn"]), **ancestor} for ancestor in ancestors],
            "toc": [{**link_passage(entry["urn"]), **entry} for entry in toc],
        }
    if isinstance(obj, cts.Collection):
        links = link_collection(str(obj.urn))
    if isinstance(obj, cts.Passage):
        links = link_passage(str(obj.urn))
        text = remaining.pop("text")
        text_ancestors = text.pop("ancestors")
        rels = {
            "text": {
                **link_collection(text["urn"]),
                "ancestors": [{**link_collection(ancestor["urn"]), **ancestor} for ancestor in text_ancestors],
                **text
            }
        }
    return {
        **links,
        **rels,
        **remaining
    }


def encode_link_header(lo: dict):
    links = []
    for rel, attrs in lo.items():
        link = []
        link.append(f"<{attrs.pop('target')}>")
        for k, v in {"rel": rel, **attrs}.items():
            link.append(f'{k}="{v}"')
        links.append("; ".join(link))
    return ", ".join(links)
