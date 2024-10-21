import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
import yaml
from github import Github
from scaife_viewer.core.hooks import hookset


GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")


class Command(BaseCommand):
    help = "Load text repos to disk"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default=settings.CTS_LOCAL_DATA_PATH,
        )

    def handle(self, *args, **options):
        repos = load_repo_list()
        dest = Path(options["path"])
        if not dest.exists():
            print(f"Creating directory {dest}")
            dest.mkdir(parents=True, exist_ok=True)

        client = Github(GITHUB_ACCESS_TOKEN)

        fs = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for repo, data in repos.items():
                f = executor.submit(load_repo, client, repo, data, dest)
                fs[f] = (repo, data["ref"])
            for f in concurrent.futures.as_completed(fs):
                repo, ref = fs[f]
                data = f.result()
                print(f"Loaded {repo} at {ref} to {data['sha']}")
                sys.stdout.flush()


def load_repo_list():
    # TODO: Make this env dependent
    content_path = hookset.content_manifest_path
    return yaml.safe_load(content_path.open())


def write_repo_metadata(metadata_path, data):
    json.dump(data, open(metadata_path, "w"), indent=2)


def load_repo(client, repo, data, dest):
    ref = data["ref"]
    sha = data["sha"]
    tarball_url = data["tarball_url"]
    safe_ref = ref.replace("/", "-")
    tarball_path = f"{repo.replace('/', '-')}-{safe_ref}-{sha[:7]}"
    absolute_tarball_path = os.path.join(dest, tarball_path)

    resp = requests.get(tarball_url, stream=True)

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        # NOTE: This handles private repos
        # TODO: Add explicit boolean to private repo in content manifest
        repo_obj = client.get_repo(repo)
        archive_url = repo_obj.get_archive_link("tarball", data["ref"])
        resp = requests.get(archive_url)
        resp.raise_for_status()

    r, w = os.pipe()
    os.makedirs(absolute_tarball_path, exist_ok=True)
    proc = subprocess.Popen(
        ["tar", "-zxf", "-", "-C", absolute_tarball_path, "--strip-components", "1"],
        stdin=r,
    )
    os.close(r)
    for chunk in resp.iter_content(chunk_size=4092):
        if chunk:
            os.write(w, chunk)
    os.close(w)
    proc.wait()

    # TODO: Convert to YAML
    metadata_path = os.path.join(absolute_tarball_path, ".scaife-viewer.json")

    data["repo"] = repo
    write_repo_metadata(metadata_path, data)
    return data
