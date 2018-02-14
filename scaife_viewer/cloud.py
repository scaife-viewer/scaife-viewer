import functools
import json
import time
import uuid

import google.auth
import requests
from google.auth.transport.requests import AuthorizedSession


class CloudJob:

    def setup(self):
        self.unique_id = str(uuid.uuid4())
        credentials, self.gce_project = google.auth.default()
        if self.gce_project is None:
            raise RuntimeError("project must be specified")
        self.gce_http = AuthorizedSession(credentials)
        self.gce_zone = query_metadata("instance/zone").split("/")[-1]
        self.gce_instance = query_metadata("instance/name")

    def handle(self, *args, **kwargs):
        if self.is_running_on_gce():
            self.setup()
            self.update_metadata(status="started")
            try:
                super().handle(*args, **kwargs)
            except Exception:
                self.update_metadata(status="failed")
                raise
            else:
                self.update_metadata(status="done")
        else:
            super().handle(*args, **kwargs)

    def is_running_on_gce(self):
        try:
            r = requests.get("http://metadata.google.internal")
        except requests.ConnectionError:
            return False
        else:
            return r.headers.get("Metadata-Flavor", "") == "Google"

    def update_metadata(self, status):
        base_url = f"https://www.googleapis.com/compute/v1/projects/{self.gce_project}/zones/{self.gce_zone}/"
        attempts = 0
        while True:
            r = self.gce_http.get(f"{base_url}instances/{self.gce_instance}")
            r.raise_for_status()
            metadata = r.json()["metadata"]
            new_metadata = {
                **{
                    item["key"]: item["value"]
                    for item in metadata["items"]
                },
                "status": status,
            }
            body = {
                "fingerprint": metadata["fingerprint"],
                "items": [
                    dict(key=key, value=value)
                    for key, value in new_metadata.items()
                ],
            }
            r = self.gce_http.post(
                f"{base_url}instances/{self.gce_instance}/setMetadata",
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
            )
            if r.ok:
                break
            if r.status_code == 412:
                attempts += 1
                if attempts == 5:
                    break
                else:
                    time.sleep(0.5)
                    continue
            r.raise_for_status()


@functools.lru_cache()
def query_metadata(key):
    url = f"http://metadata.google.internal/computeMetadata/v1/{key}"
    headers = {
        "Metadata-Flavor": "Google",
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        raise KeyError(key)
    r.raise_for_status()
    return r.text
