from sv_pdl.atlas.extractors.attributions import extract_attributions
from sv_pdl.atlas.extractors.source_repos import set_upstream_repo_names


def extract_atlas_annotations(reset=False):
    extract_attributions()


def prefer_source_repo_names(reset=False):
    set_upstream_repo_names()
