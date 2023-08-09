# -*- coding: utf-8 -*-
"""
Extract attribution data CTS-Compliant TEI XML
"""
import json
import logging
import os
import re
from collections import Counter, OrderedDict, defaultdict

import yaml
from scaife_viewer.atlas import constants
from scaife_viewer.atlas.conf import settings
from scaife_viewer.atlas.models import Node, Repo


logger = logging.getLogger(__name__)

ANNOTATIONS_DATA_PATH = os.path.join(
    settings.SV_ATLAS_DATA_DIR, "annotations", "attributions"
)
STATS_DATA_PATH = os.path.join(
    settings.SV_ATLAS_DATA_DIR,
    "stats",
)

OGL_CONFIG_PATH = os.path.join(
    settings.SV_ATLAS_DATA_DIR, "config", "OpenGreekAndLatin--First1KGreek--config.yml"
)


def tei(name):
    return "{http://www.tei-c.org/ns/1.0}" + name


def ws(s):
    return re.sub(r"\s+", " ", s.strip())


def get_cts_resolver():
    # NOTE: This will perform poorly against the API resolver
    from scaife_viewer.core.cts.capitains import default_resolver

    return default_resolver()


def get_tei_xml(resolver, urn):
    return resolver.getTextualNode(urn).xml


def extract_publication_statement(xml_obj):
    try:
        return list(iter(xml_obj.teiHeader.fileDesc.publicationStmt))[0]
    except AttributeError as e:
        logger.debug(e)
        return None


def extract_resp_statements(xml_obj):
    try:
        return list(iter(xml_obj.teiHeader.fileDesc.titleStmt.respStmt))
    except AttributeError as e:
        logger.debug(e)
        return None


def process_publication_statement(lookup, urn, publication_statement):
    value = None
    publisher_or_authority = getattr(
        publication_statement,
        "publisher",
        getattr(publication_statement, "authority", None),
    )
    if publisher_or_authority is not None:
        value = "".join(publisher_or_authority.itertext()).strip()

    if value:
        lookup[urn].append([[], ["Publisher"], [value], []])
    else:
        msg = f'No publisher [urn="{urn}"]'
        logger.error(msg)


def process_resp_statements(lookup, urn, resp_statements):
    for child in resp_statements:
        persName = []
        resp = []
        orgName = []
        name = []
        for gchild in child.iterchildren():
            if gchild.tag == tei("persName"):
                if list(gchild.iterchildren()):
                    persName.append(ws(" ".join(gchild.xpath(".//text()"))))
                else:
                    persName.append(gchild.text.strip())
            elif gchild.tag == tei("resp"):
                assert not list(gchild.iterchildren())
                resp.append(ws(gchild.text))
            elif gchild.tag == tei("orgName"):
                assert not list(gchild.iterchildren())
                if gchild.text:
                    orgName.append(ws(gchild.text))
                else:
                    pass  # @@@
            elif gchild.tag == tei("name"):
                assert len(list(gchild.iterchildren())) == 0
                if gchild.text:
                    name.append(ws(gchild.text))
                else:
                    pass  # @@@
            else:
                logger.debug(gchild.tag)
                # quit()
        lookup[urn].append([persName, resp, orgName, name])
        logger.debug(persName)
        logger.debug(resp)
        logger.debug(orgName)
        logger.debug(name)


def build_attributions_lookup(resolver, versions):
    # TODO: Expose proper edge-case support
    edgecases = {
        # https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/549552146ad00e60b065bd22e3935cdcdf529b4d/data/phi0914/phi001/phi0914.phi001.perseus-lat2.xml
        "urn:cts:latinLit:phi0914.phi001.perseus-lat2:",
    }

    lookup = defaultdict(list)
    for version in versions:
        urn = version.urn

        if urn in edgecases:
            continue

        safe_urn = urn[:-1]
        xml_obj = get_tei_xml(resolver, safe_urn)

        publication_statement = extract_publication_statement(xml_obj)
        if publication_statement is not None:
            process_publication_statement(lookup, urn, publication_statement)

        resp_statements = extract_resp_statements(xml_obj)
        if resp_statements:
            process_resp_statements(lookup, urn, resp_statements)
    return lookup


def get_weight(promoted_roles_lookup, role):
    weight = promoted_roles_lookup.get(role, 0)
    return weight


def get_attributions_config(config_file_path):
    with open(config_file_path) as f:
        data = yaml.load(f.read(), Loader=yaml.SafeLoader)
    return data.get("attributions")


def get_substitutions(config):
    substitutions = {}
    for record in config.get("substitutions", []):
        match = record["match"]
        name_key = tuple([n for n in match.get("names", []) if n])
        org_key = tuple(e for e in match.get("orgs", []) if e)
        compound_key = (match["role"], name_key, org_key)
        substitutions[compound_key] = record["data"]
    return substitutions


def get_promoted_roles_lookup(config):
    promoted = config.get("promoted", [])
    promoted.reverse()
    roles_lookup = OrderedDict()
    for pos, entry in enumerate(promoted):
        roles_lookup[entry] = (pos + 1) * -1
    return roles_lookup


class AttributionAnnotationConverter:
    def __init__(self, config, lookup):
        self.substitutions = get_substitutions(config)
        self.promoted_roles_lookup = get_promoted_roles_lookup(config)
        self.lookup = lookup

    def process_substitution(self, annotations, urn, remap_key, weight):
        for replacement in self.substitutions[remap_key]:
            record = dict(data=dict(references=[urn], weight=weight))
            record.update(replacement)
            annotations.append(record)
        return

    def process_orgs_only_row(self, urn, role, weight, orgs, annotations):
        for org in orgs:
            record = dict(
                role=role,
                person=None,
                organization=dict(name=org),
                data=dict(references=[urn], weight=weight),
            )
            annotations.append(record)
        return

    def process_name_org_pairs(self, urn, role, weight, names, orgs, annotations):
        for name, org in zip(names, orgs):
            record = dict(
                role=role,
                person=dict(name=name),
                organization=dict(name=org),
                data=dict(references=[urn], weight=weight),
            )
            annotations.append(record)
        return

    def process_names_and_orgs(self, urn, role, weight, names, orgs, annotations):
        for org in orgs:
            record = dict(
                role=role,
                person=None,
                organization=dict(name=org),
                data=dict(references=[urn], weight=weight),
            )
            annotations.append(record)
        for name in names:
            person = {
                "name": name,
            }
            record = dict(
                role=role,
                person=person,
                organization=None,
                data=dict(references=[urn], weight=weight),
            )
            annotations.append(record)

    def process_row(self, urn, row, annotations):
        # @@@ getlist type functionality for persons and organizations
        role = row[1][0]
        orgs = [o.strip() for o in row[2] if o.strip]
        names = [n.strip() for n in row[0] + row[3] if n.strip]
        weight = get_weight(self.promoted_roles_lookup, role)

        remap_key = (role, tuple(names), tuple(orgs))
        if remap_key in self.substitutions:
            return self.process_substitution(annotations, urn, remap_key, weight)
        elif not names and orgs:
            return self.process_orgs_only_row(urn, role, weight, orgs, annotations)
        elif len(names) == len(orgs):
            return self.process_name_org_pairs(
                urn, role, weight, names, orgs, annotations
            )
        else:
            return self.process_names_and_orgs(
                urn, role, weight, names, orgs, annotations
            )

    def postprocess_rows(self, annotations):
        # post-processing
        annotations = sorted(
            annotations, key=lambda x: x.get("data", {}).get("weight", 0)
        )
        for record in annotations:
            record["data"].pop("weight")
        return annotations

    def create_annotations(self, urn, data):
        annotations = []
        for row in data:
            self.process_row(urn, row, annotations)
        return self.postprocess_rows(annotations)

    def create_attribution_annotations(self):
        all_annotations = []
        for urn, data in self.lookup.items():
            all_annotations.extend(self.create_annotations(urn, data))
        return all_annotations


def prepare_atlas_annotations(config, lookup):
    if config is None:
        config = {}
    converter = AttributionAnnotationConverter(config, lookup)
    return converter.create_attribution_annotations()


def generate_attribution_stats(attributions):
    org_counter = Counter()
    person_counter = Counter()
    role_counter = Counter()
    urn_counter = Counter()
    for attribution in attributions:
        organization = attribution["organization"]
        if organization:
            org_counter[organization["name"]] += 1
        person = attribution["person"]
        if person:
            person_counter[person["name"]] += 1
        role_counter[attribution["role"]] += 1
        urn = attribution["data"]["references"][0]
        urn_counter[urn] += 1
    return dict(
        organizations=org_counter,
        people=person_counter,
        roles=role_counter,
        urns=urn_counter,
    )


def write_annotations(name, attributions):
    os.makedirs(ANNOTATIONS_DATA_PATH, exist_ok=True)
    file_name = os.path.join(ANNOTATIONS_DATA_PATH, f"{name}.json")
    with open(file_name, "w") as f:
        json.dump(attributions, f, ensure_ascii=False, indent=2)


def write_stats(source, stats):
    os.makedirs(STATS_DATA_PATH, exist_ok=True)
    file_name = os.path.join(STATS_DATA_PATH, f'{source["name"]}-attributions.json')

    with open(file_name, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def extract_attributions(include_stats=False):
    # TODO: filter by repo or URN
    resolver = get_cts_resolver()
    version_qs = Node.objects.filter(depth=constants.CTS_URN_DEPTHS["version"])

    # TODO: Split sources by repo based on presence of config files
    ogl_1kgrc_repo = Repo.objects.filter(name="OpenGreekAndLatin/First1KGreek").first()

    ogl_1kgrc_versions = version_qs.filter(repos__in=[ogl_1kgrc_repo])
    other_versions = version_qs.exclude(repos__in=[ogl_1kgrc_repo])
    sources = [dict(qs=other_versions, name="other", config_path=None)]
    if ogl_1kgrc_repo:
        sources.append(
            dict(
                qs=ogl_1kgrc_versions,
                name="1kgrc",
                # TODO: derive queryset and config from repo root
                # or another optional config path
                config_path=OGL_CONFIG_PATH,
            )
        )

    for source in sources:
        lookup = build_attributions_lookup(resolver, source["qs"])
        config_path = source.get("config_path")
        if config_path:
            config = get_attributions_config(config_path)
        else:
            config = None

        attributions = prepare_atlas_annotations(config, lookup)
        write_annotations(source["name"], attributions)

        if include_stats:
            stats = generate_attribution_stats(attributions)
            write_stats(source, stats)
