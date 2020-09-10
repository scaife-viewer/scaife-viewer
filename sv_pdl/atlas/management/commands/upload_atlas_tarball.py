import os
import shlex
import subprocess

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Compresses / uploads an ATLAS database tarball
    """

    help = "Compresses / uploads an ATLAS database tarball"

    @staticmethod
    def do_shell_command(command_string):
        result = subprocess.run(shlex.split(command_string), capture_output=True)
        result.check_returncode()
        return result.stdout.decode("utf-8")

    def handle(self, *args, **options):
        database_path = settings.SV_ATLAS_DB_PATH

        if database_path is None:
            msg = "The SV_ATLAS_DB_PATH setting is missing and is required for this management command to work."
            raise ImproperlyConfigured(msg)

        self.stdout.write(
            "--[Creating / uploading database tarball]--"
        )

        database_file = os.path.basename(database_path)
        result = self.do_shell_command(f"md5sum {database_path}")
        md5sha = result.split(" ")[0]
        self.stdout.write(f"{database_path} md5 sha: {md5sha}")

        database_dir = os.path.dirname(database_path)
        os.chdir(database_dir)

        compressed_db_filename = f"db-{md5sha}.tgz"
        self.stdout.write(f"Compressing {database_path} as {compressed_db_filename} ")
        tar_cmd = f"tar -cvzf {compressed_db_filename} {database_file}"
        self.do_shell_command(tar_cmd)

        bucket = "atlas-db-tarballs"
        site = "sv-pdl"
        self.stdout.write(f"Uploading {compressed_db_filename} to {bucket}")
        gsutil_cmd = f"gsutil -m cp -a public-read {compressed_db_filename} gs://{bucket}/{site}/{compressed_db_filename}"
        self.do_shell_command(gsutil_cmd)

        url = f"https://storage.googleapis.com/{bucket}/{site}/{compressed_db_filename}"
        self.stdout.write(f"Uploaded to {url}")

        self.stdout.write(f"Removing {compressed_db_filename}")
        rm_cmd = f"rm {compressed_db_filename}"
        self.do_shell_command(rm_cmd)

        self.stdout.write(f"Writing {url} to .atlas-db-url")
        atlas_db_url_path = os.path.join(
            settings.PROJECT_ROOT,
            ".atlas-db-url"
        )
        with open(atlas_db_url_path, "w") as f:
            f.write(url)
        self.stdout.write("--[Done!]--")

        # NOTE: run export ATLAS_DB_URL=$(cat .atlas-db-url)
        # to populate $ATLAS_DB_URL
