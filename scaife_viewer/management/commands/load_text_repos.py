import json
import os
import re
import subprocess
import sys

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
        repos = {
            "PerseusDL/canonical-latinLit": "master",
            "PerseusDL/canonical-greekLit": "master",
            "OpenGreekAndLatin/csel-dev": "master",
            "PerseusDL/canonical-farsiLit": "master",
            "PerseusDL/canonical-pdlpsci": "master",
            "PerseusDL/canonical-pdlrefwk": "master",
            "OpenGreekAndLatin/First1KGreek": "master",
            "lascivaroma/priapeia": "master",
            "hlapin/ancJewLitCTS": "master",
        }
        resolved = {}
        root_dir = options["path"]
        for repo, ref in repos.items():
            sha = resolve_commit(repo, ref)
            load_repo(
                f"https://api.github.com/repos/{repo}/tarball/{sha}",
                os.path.join(root_dir, "data"),
            )
            resolved[repo] = sha
            print(f"Loaded {repo} at {ref} to {sha}")
            sys.stdout.flush()

        with open(os.path.join(root_dir, "repos.json"), "w") as f:
            f.write(json.dumps(resolved))


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


def resolve_commit(repo, ref):
    if re.match(r"^[a-f0-9]{40}$", ref):
        return ref
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{ref}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.get(ref_url, headers=headers)
    if resp.status_code == 404:
        tag_url = f"https://api.github.com/repos/{repo}/git/tags/{ref}"
        resp = requests.get(tag_url, headers=headers)
        if resp.status_code == 404:
            raise Exception(f"{repo}: ref ({ref}) not found")
        else:
            resp.raise_for_status()
            ref_obj = resp.json()["object"]
    else:
        resp.raise_for_status()
        ref_obj = resp.json()["object"]
    return ref_obj["sha"]
