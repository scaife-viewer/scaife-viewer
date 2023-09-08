from pathlib import Path

from django.conf import settings

import regex
from scaife_viewer.atlas.hooks import DefaultHookSet, _get_annotation_paths
from scaife_viewer.atlas.resolvers.cts_collection import (
    resolve_cts_collection_library,
)
from scaife_viewer.core.cts import text_inventory


PROBLEM_URNS = [urn for urn in """
urn:cts:greekLit:tlg0019.tlg006.perseus-eng1
urn:cts:greekLit:tlg0074.tlg001.perseus-grc1
urn:cts:greekLit:tlg0074.tlg002.perseus-grc1
urn:cts:greekLit:tlg0074.tlg003.perseus-grc1
urn:cts:greekLit:tlg0074.tlg004.perseus-grc1
urn:cts:greekLit:tlg0074.tlg005.perseus-grc1
urn:cts:greekLit:tlg0074.tlg006.perseus-grc1
urn:cts:greekLit:tlg0093.tlg009.perseus-grc1
urn:cts:greekLit:tlg0612.tlg001.perseus-grc1
urn:cts:greekLit:tlg3135.tlg001.opp-grc3
urn:cts:latinLit:phi0474.phi051.perseus-eng1
urn:cts:latinLit:phi0474.phi053.perseus-eng1
urn:cts:latinLit:phi0474.phi055.perseus-eng1
urn:cts:perslit:anvari.divan.pdl
urn:cts:perslit:attar.divan.pdl
urn:cts:perslit:babataher.divan.pdl
urn:cts:perslit:bidel.divan.pdl
urn:cts:perslit:eraghi.divan.pdl
urn:cts:perslit:farrokhi.divan.pdl
urn:cts:perslit:feyz.divan.pdl
urn:cts:perslit:ghaani.divan.pdl
urn:cts:perslit:hafez.divan.pdl
urn:cts:perslit:hatef.divan.pdl
urn:cts:perslit:helali.divan.pdl
urn:cts:perslit:hojviri.kashfol-mahjoob.pdl
urn:cts:perslit:jami.7ourang.pdl
urn:cts:perslit:khaghani.divan.pdl
urn:cts:perslit:khalili.divan.pdl
urn:cts:perslit:mahsati.divan.pdl
urn:cts:perslit:mohtasham.divan.pdl
urn:cts:perslit:monshi.kelile-demni.pdl
urn:cts:perslit:naserkhosro.safarname.pdl
urn:cts:perslit:obeyd.divan.pdl
urn:cts:perslit:orfi.divan.pdl
urn:cts:perslit:parvin.divan.pdl
urn:cts:perslit:rahi.divan.pdl
urn:cts:perslit:razi.divan.pdl
urn:cts:perslit:roodaki.masnavi.pdl
urn:cts:perslit:saeb.divan.pdl
urn:cts:perslit:salman.divan.pdl
urn:cts:perslit:seyf.divan.pdl
urn:cts:perslit:shahnematollah.divan.pdl
urn:cts:perslit:shater.divan.pdl
urn:cts:perslit:vahshi.divan.pdl
""".splitlines() if urn]

PERSLIT_NS = "urn:cts:perslit:"


THUCYDIDES_TEXTGROUP_REGEX = r"urn:cts:greekLit:tlg0003\."
LOWEST_TEXTPARTS_TEXTGROUPS_REGEX = regex.compile(rf"{THUCYDIDES_TEXTGROUP_REGEX}")


class ATLASHookSet(DefaultHookSet):
    def resolve_library(self):
        ti = text_inventory()
        return resolve_cts_collection_library(ti)

    def should_ingest_lowest_citable_nodes(self, cts_version_obj):
        return LOWEST_TEXTPARTS_TEXTGROUPS_REGEX.match(cts_version_obj.urn)

    def get_first_passage_urn(self, version):
        version_urn = str(version.urn)
        if version_urn in PROBLEM_URNS:
            # MyCapytain is unable to extract the first
            # passage URN, so better to just skip processing them.
            return None
        elif version_urn.startswith(PERSLIT_NS):
            # perslit versions take a long time to
            # process for TOC purposes
            # FIXME: Improve TOC performance for these URNs
            return None
        return super().get_first_passage_urn(version)

    def extract_cts_textpart_metadata(self, version):
        # NOTE: We don't yet use ATLAS to resolve anything past the version-text
        # level, so we can safely skip this.
        return {}

    def get_dictionary_annotation_paths(self):
        # FIXME: improve discovery
        subdir = "scaife-viewer-ogl-pdl-annotations-532d1bd-532d1bd/data/dictionaries"
        path = Path(settings.SV_ATLAS_DATA_DIR, "annotations", subdir)
        # FIXME: Standardize "default" annotation formats; currently we have a mixture
        # of manifest or "all-in-one" files that makes things inconsistent
        predicate = lambda x: x.suffix == ".json" or x.is_dir()  # noqa
        return _get_annotation_paths(path, predicate=predicate)
