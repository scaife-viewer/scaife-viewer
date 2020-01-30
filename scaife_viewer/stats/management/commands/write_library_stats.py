import json
from collections import Counter, defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.functional import cached_property

from .... import cts
from ....search import es

from ... import LIBRARY_STATS_PATH


class Command(BaseCommand):

    help = "Generate library statistics"

    def calculate_word_counts(self):
        body = {
            "aggs": {
                "language": {
                    "terms": {
                        "field": "language"
                    },
                    "aggs": {
                        "word_count": {
                            "sum": {
                                "field": "word_count"
                            }
                        }
                    }
                }
            }
        }
        aggregations = es.search(index=settings.ELASTICSEARCH_INDEX_NAME, body=body, params=dict(size=0))["aggregations"]
        buckets = aggregations["language"]["buckets"]
        marquee_languages = {
            "grc": "Greek",
            "lat": "Latin"
        }
        lookup = defaultdict(int)
        for entry in buckets:
            lookup["total"] += int(entry["word_count"]["value"])
            if entry["key"] in marquee_languages:
                lookup[entry["key"]] += int(entry["word_count"]["value"])
        return lookup

    @cached_property
    def inventory_stats(self):
        text_groups = []
        works = []
        texts = []
        all_text_groups = cts.text_inventory().text_groups()
        for text_group in all_text_groups:
            for work in text_group.works():
                works.append(work)
                for text in work.texts():
                    texts.append(text)
            text_groups.append(text_group)

        text_language_counts = Counter()
        for text in texts:
            # @@@ resolve pers issue
            if text.lang == "None":
                key = "pers"
            else:
                key = text.lang
            text_language_counts[key] += 1
        return {
            "works_count": len(works),
            "texts_count": len(texts),
            "grc_texts_count": text_language_counts["grc"],
            "lat_texts_count": text_language_counts["lat"]
        }

    def handle(self, *args, **options):
        stats = {}
        stats["works_count"] = self.inventory_stats["works_count"]
        stats["word_counts"] = self.calculate_word_counts()
        stats["text_counts"] = {
            "total": self.inventory_stats["texts_count"],
            "grc": self.inventory_stats["grc_texts_count"],
            "lat": self.inventory_stats["lat_texts_count"],
        }
        with open(LIBRARY_STATS_PATH, "w") as f:
            json.dump(stats, f, indent=2, sort_keys=True)
