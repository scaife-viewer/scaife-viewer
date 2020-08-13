import concurrent.futures
import os
import subprocess
import sys
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand

import requests


class Command(BaseCommand):

    help = "Load text repos to disk"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default="/var/lib/nautilus",
        )

    def handle(self, *args, **options):
        repos = load_repo_list()
        root_dir = options["path"]
        dest = os.path.join(root_dir, "data")
        if not os.path.exists(dest):
            print(f"Creating directory {dest}")
            os.makedirs(dest)
        fs = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for repo, data in repos.items():
                sha = data["sha"]
                tarball_url = f"https://api.github.com/repos/{repo}/tarball/{sha}"
                f = executor.submit(load_repo, tarball_url, dest)
                fs[f] = (repo, sha)
            for f in concurrent.futures.as_completed(fs):
                repo, sha = fs[f]
                f.result()
                print(f"Loaded {repo} to {sha}")
                sys.stdout.flush()


def load_repo_list():
    parsed = urlparse(settings.CTS_API_ENDPOINT)
    r = requests.get(f"{parsed.scheme}://{parsed.netloc}/repos")
    r.raise_for_status()
    return r.json()


def load_repo(tarball_url, dest):
    resp = requests.get(tarball_url, stream=True)
    resp.raise_for_status()
    r, w = os.pipe()
    proc = subprocess.Popen(["tar", "-zxf", "-", "-C", dest], stdin=r)
    os.close(r)
    for chunk in resp.iter_content(chunk_size=4092):
        if chunk:
            os.write(w, chunk)
    os.close(w)
    proc.wait()
