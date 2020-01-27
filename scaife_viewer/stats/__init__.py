import os
import json

from django.core.cache import cache
from django.contrib.humanize.templatetags.humanize import intword, intcomma

LIBRARY_STATS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "library_stats.json"
)


def get_library_stats():
    """
    Loads library stats as computed via `write_library_stats` management command.

    In the future, these stats may be served up directly from `scaife-cts-api`
    at the conclusion of indexing.  For now, `scaife-viewer` seens to be the most
    sensible place to compute the stats since it has the connection info for both
    Nautilus and ElasticSearch.
    """
    key = "library-stats"
    library_stats = cache.get(key, None)
    if library_stats is None:
        data = json.load(open(LIBRARY_STATS_PATH))
        library_stats = {
            "works_count": intcomma(data["works_count"]),
            "text_counts_total": intcomma(data["text_counts"]["total"]),
            "text_counts_greek": intcomma(data["text_counts"]["grc"]),
            "text_counts_latin": intcomma(data["text_counts"]["lat"]),
            "word_counts_total": intword(data["word_counts"]["total"]).split(" ")[0],
            "word_counts_greek": intword(data["word_counts"]["grc"]).split(" ")[0],
            "word_counts_latin": intword(data["word_counts"]["lat"]).split(" ")[0]
        }
        cache.set(key, library_stats, None)
    return library_stats
