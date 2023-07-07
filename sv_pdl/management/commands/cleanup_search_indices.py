from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

from scaife_viewer.core.search import get_es_client as elasticsearch_client


class Command(BaseCommand):
    """
    Cleans up old search indices
    """

    help = "Cleans up old search indices"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force deletion (no prompt).",
        )

    def handle(self, *args, **options):
        force = options["force"]
        es = elasticsearch_client()
        idx = settings.ELASTICSEARCH_INDEX_NAME
        self.stdout.write(f"Primary index: {idx}")
        all_indices = set([i for i in es.indices.get("*").keys()])
        assert idx in all_indices
        to_delete = all_indices.difference({idx})
        if to_delete:
            deletes_string = "\n\t".join(to_delete)
            self.stdout.write(f"Indices to delete:\n {deletes_string}")
            delete_indices = force or input("Delete indices? [y/n]\n") == "y"
            if delete_indices:
                deleted = es.indices.delete(index=",".join(to_delete))
                assert deleted
                self.stdout.write(f"Indices deleted: {len(to_delete)} ")
        else:
            self.stdout.write("No indices to delete")

        current_indices = set([i for i in es.indices.get("*").keys()])
        assert set([idx]) == current_indices
