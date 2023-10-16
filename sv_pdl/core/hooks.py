from pathlib import Path
from scaife_viewer.core.hooks import DefaultHookSet


class CoreHookSet(DefaultHookSet):
    @property
    def content_manifest_path(self):
        # FIXME:
        return Path("data/content-manifests/local.yaml")
