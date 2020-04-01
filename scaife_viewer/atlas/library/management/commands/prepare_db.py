import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...library import importers


class Command(BaseCommand):
    """
    Prepares the database
    """

    help = "Prepares the database"

    def handle(self, *args, **options):
        pass
        # if os.path.exists("db.sqlite3"):
        #     os.remove("db.sqlite3")
        #     self.stdout.write("--[Removed existing database]--")

        # self.stdout.write("--[Creating database]--")
        # call_command("migrate")

        # self.stdout.write("--[Loading versions]--")
        # importers.import_versions()
