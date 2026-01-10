from pathlib import Path
from scaife_viewer.core.hooks import DefaultHookSet


class CoreHookSet(DefaultHookSet):
    @property
    def content_manifest_path(self):
        # FIXME:
        return Path("data/content-manifests/local.yaml")

    @property
    def enable_canonical_pdlrefwk_flags(self):
        # NOTE: Setting this to `False` will allow us to consume
        # the lower refsDecls on Marchant, but Greenough will not
        # load consistently.
        return False
