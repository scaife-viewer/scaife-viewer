from collections import Counter

from django.core.management.base import BaseCommand

from ... import cts


class Command(BaseCommand):

    help = "Print library statistics"

    def handle(self, *args, **options):
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

        self.stdout.write(f"Text Group Count: {len(text_groups)}")
        self.stdout.write(f"Work Count: {len(works)}")
        self.stdout.write(f"Text Count: {len(texts)}")
        self.stdout.write("Text Count By Language:")

        text_language_counts = Counter()
        for text in texts:
            # @@@ resolve pers issue
            if text.lang == "None":
                key = "pers"
            else:
                key = text.lang
            text_language_counts[key] += 1

        for lang, count in text_language_counts.most_common():
            self.stdout.write(f"  {lang}: {count}")
