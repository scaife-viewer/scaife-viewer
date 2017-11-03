from django.core.urlresolvers import reverse

from . import cts


def apify(collection):
    remaining_collection = collection.as_json()
    rels = {}
    if isinstance(collection, cts.TextGroup):
        works = remaining_collection.pop("works")
        rels = {
            "works": [
                {
                    "url": reverse("library_collection", kwargs={"urn": work["urn"]}),
                    "json_url": reverse("library_collection_json", kwargs={"urn": work["urn"]}),
                    **work
                }
                for work in works
            ],
        }
    if isinstance(collection, cts.Work):
        texts = remaining_collection.pop("texts")
        rels = {
            "texts": [
                {
                    "url": reverse("library_collection", kwargs={"urn": text["urn"]}),
                    "json_url": reverse("library_collection_json", kwargs={"urn": text["urn"]}),
                    **text
                }
                for text in texts
            ],
        }
    if isinstance(collection, cts.Text):
        first_passage = remaining_collection.pop("first_passage")
        ancestors = remaining_collection.pop("ancestors")
        toc = remaining_collection.pop("toc")
        rels = {
            "first_passage": {
                "url": reverse("reader", kwargs={"urn": first_passage["urn"]}),
                "json_url": reverse("library_passage_json", kwargs={"urn": first_passage["urn"]}),
                **first_passage
            },
            "ancestors": [
                {
                    "url": reverse("library_collection", kwargs={"urn": ancestor["urn"]}),
                    "json_url": reverse("library_collection_json", kwargs={"urn": ancestor["urn"]}),
                }
                for ancestor in ancestors
            ],
            "toc": [
                {
                    "url": reverse("reader", kwargs={"urn": entry["urn"]}),
                    "json_url": reverse("library_passage_json", kwargs={"urn": entry["urn"]}),
                    **entry
                }
                for entry in toc
            ],
        }
    return {
        "url": reverse("library_collection", kwargs={"urn": str(collection.urn)}),
        "json_url": reverse("library_collection_json", kwargs={"urn": str(collection.urn)}),
        **rels,
        **remaining_collection
    }
