import concurrent.futures
import json
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
                f = executor.submit(load_repo, repo, data, dest)
                fs[f] = (repo, data["ref"])
            for f in concurrent.futures.as_completed(fs):
                repo, ref = fs[f]
                data = f.result()
                print(f"Loaded {repo} at {ref} to {data['sha']}")
                sys.stdout.flush()


def load_repo_list():
    parsed = urlparse(settings.CTS_API_ENDPOINT)
    r = requests.get(f"{parsed.scheme}://{parsed.netloc}/repos")
    r.raise_for_status()
    return r.json()


def write_repo_metadata(metadata_path, data):
    json.dump(data, open(metadata_path, "w"), indent=2)


def load_repo(repo, data, dest):
    ref = data["ref"]
    sha = data["sha"]
    tarball_url = data["tarball_url"]
    tarball_path = f"{repo.replace('/', '-')}-{ref}-{sha[:7]}"
    absolute_tarball_path = os.path.join(dest, tarball_path)

    resp = requests.get(tarball_url, stream=True)
    resp.raise_for_status()
    r, w = os.pipe()
    os.makedirs(absolute_tarball_path, exist_ok=True)
    proc = subprocess.Popen(["tar", "-zxf", "-", "-C", absolute_tarball_path, "--strip-components", "1"], stdin=r)
    os.close(r)
    for chunk in resp.iter_content(chunk_size=4092):
        if chunk:
            os.write(w, chunk)
    os.close(w)
    proc.wait()

    metadata_path = os.path.join(absolute_tarball_path, ".scaife-viewer.json")
    write_repo_metadata(metadata_path, data)
    return data
