from scaife_viewer.atlas.hooks import DefaultHookSet
from scaife_viewer.atlas.resolvers.cts_collection import (
    resolve_cts_collection_library,
)
from scaife_viewer.core.cts import text_inventory
from scaife_viewer.core.cts.exceptions import InvalidPassageReference


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


class ATLASHookSet(DefaultHookSet):
    def resolve_library(self):
        ti = text_inventory()
        return resolve_cts_collection_library(ti)

    def should_ingest_lowest_citable_nodes(self, cts_version_obj):
        # NOTE: We don't yet use ATLAS to resolve anything past the version-text
        # level, so we can safely skip this.
        return False

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
        try:
            return super().get_first_passage_urn(version)
        except InvalidPassageReference as err:
            print(err)
            return None

    def extract_cts_textpart_metadata(self, version):
        # NOTE: We don't yet use ATLAS to resolve anything past the version-text
        # level, so we can safely skip this.
        return {}
