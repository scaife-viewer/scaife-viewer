from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from sv_pdl.atlas.extractors.attributions import extract_attributions


class Command(BaseCommand):
    """
    Extracts ATLAS annotations from corpora
    """

    help = "Extracts ATLAS annotations from corpora"

    def handle(self, *args, **options):
        # TODO: add fetch_corpus_repo_metadata to this pipeline
        self.stdout.write("--[Extracting attributions]--")
        extract_attributions()
