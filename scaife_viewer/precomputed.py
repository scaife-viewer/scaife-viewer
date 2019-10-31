"""
This module is used to pre-compute expensive operations when the web server boots up.
"""
from django.core.cache import cache

from . import cts
from .utils import apify


def library_view_json():
    key = "library-view-json"
    data = cache.get(key, None)
    if data is None:
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
        data = {
            "text_groups": [apify(text_group) for text_group in text_groups],
            "works": [apify(work) for work in works],
            "texts": [apify(text) for text in texts],
        }
        cache.set(key, data, None)
    return data
