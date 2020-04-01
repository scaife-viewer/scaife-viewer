import json
import os
import re
import sys
from collections import defaultdict

from django.conf import settings
from django.db.models import Max
from django.utils.translation import ugettext_noop

from treebeard.exceptions import PathOverflow

from scaife_viewer import cts

from .. import constants
from .models import Node
from .urn import URN


LIBRARY_DATA_PATH = os.path.join(settings.PROJECT_ROOT, "data", "library")


def get_lang_value(value):
    if re.match(r"^[a-z]+-[A-Z][a-z]+$", value):
        return value.split("-")[0]
    else:
        return value


class CTSCollectionResolver:
    def __init__(self):
        self.text_groups = {}
        self.works = {}
        self.versions = {}
        self.resolved = self.resolve_tei_xml()

    def get_text_group_metadata(self, text_group):
        """
            {
                "urn": "urn:cts:greekLit:tlg0012:",
                "node_kind": "textgroup",
                "name": [
                    {
                    "lang": "eng",
                    "value": "Homer"
                    }
                ]
            }
        """
        return dict(
            urn=f"{text_group.urn}:",
            node_kind="textgroup",
            name=[dict(lang="eng", value=str(text_group.label))],
        )

    def get_work_metadata(self, work):
        """
            {
                "urn": "urn:cts:greekLit:tlg0012.tlg001:",
                "group_urn": "urn:cts:greekLit:tlg0012:",
                "node_kind": "work",
                "lang": "grc",
                "title": [
                    {
                    "lang": "eng",
                    "value": "Iliad"
                    }
                ],
                "versions": [
                    {
                    "urn": "urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:",
                    "node_kind": "version",
                    "version_kind": "edition",
                    "first_passage_urn": "urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:1.1-1.7",
                    "citation_scheme": ["book", "line"],
                    "label": [
                        {
                        "lang": "eng",
                        "value": "Iliad (Greek Text of Munro & Allen)"
                        }
                    ],
                    "description": [
                        {
                        "lang": "eng",
                        "value": "Homer, creator; Monro, D. B. (David Binning), 1836-1905, creator; Monro, D. B. (David Binning), 1836-1905, editor; Allen, Thomas W. (Thomas William), b. 1862, editor"
                        }
                    ]
                    }
                ]
            }
        """
        return dict(
            urn=f"{work.urn}:",
            # @@@
            group_urn=f'{work.urn.rsplit(".", maxsplit=1)[0]}:',
            node_kind="work",
            lang=get_lang_value(work.metadata.lang),
            # @@@ label vs title wa
            title=[
                {
                    # @@@ hacky
                    "lang": work.label._language,
                    "value": str(work.label),
                }
            ],
        )

    def get_version_metadata(self, version):
        return dict(
            urn=f"{version.urn}:",
            node_kind="version",
            version_kind=version.kind,
            # @@@
            # first_passage_urn
            citation_scheme=[c.name for c in version.metadata.citation],
            label=[
                {
                    # @@@ hacky
                    "lang": version.label._language,
                    "value": str(version.label),
                }
            ],
            description=[
                {
                    # @@@ hacky
                    "lang": version.description._language,
                    "value": str(version.description),
                }
            ],
            lang=get_lang_value(version.metadata.lang),
        )

    def resolve_versions(self, work):
        """
        {
        "urn": "urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:",
        "node_kind": "version",
        "version_kind": "edition",
        "first_passage_urn": "urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:1.1-1.7",
        "citation_scheme": ["book", "line"],
        "label": [
            {
            "lang": "eng",
            "value": "Iliad (Greek Text of Munro & Allen)"
            }
        ],
        "description": [
            {
            "lang": "eng",
            "value": "Homer, creator; Monro, D. B. (David Binning), 1836-1905, creator; Monro, D. B. (David Binning), 1836-1905, editor; Allen, Thomas W. (Thomas William), b. 1862, editor"
            }
        ]
        }
        """
        for version in work.texts():
            version_metadata = self.get_version_metadata(version)
            self.versions[version_metadata["urn"]] = version_metadata

    def resolve_works(self, text_group):
        for work in text_group.works():
            if work.urn.count(" ") > 0:
                # @@@ defensive coding around bad URNs
                continue
            work_metadata = self.get_work_metadata(work)
            self.works[work_metadata["urn"]] = work_metadata
            self.resolve_versions(work)

    def resolve_tei_xml(self):
        for text_group in cts.text_inventory().text_groups():
            text_group_metadata = self.get_text_group_metadata(text_group)
            self.text_groups[text_group_metadata["urn"]] = text_group_metadata
            self.resolve_works(text_group)
        return self.text_groups, self.works, self.versions


class LibraryDataResolver:
    def __init__(self, data_dir_path):
        self.text_groups = {}
        self.works = {}
        self.versions = {}
        self.resolved = self.resolve_data_dir_path(data_dir_path)

    def populate_versions(self, dirpath, data):
        for version in data:
            version_part = version["urn"].rsplit(":", maxsplit=2)[1]
            version_path = os.path.join(dirpath, f"{version_part}.txt")

            if not os.path.exists(version_path):
                raise FileNotFoundError(version_path)

            self.versions[version["urn"]] = {"path": version_path, **version}

    def resolve_data_dir_path(self, data_dir_path):
        for dirpath, dirnames, filenames in sorted(os.walk(data_dir_path)):
            if "metadata.json" not in filenames:
                continue

            metadata = json.load(open(os.path.join(dirpath, "metadata.json")))
            assert metadata["node_kind"] in ["textgroup", "work"]

            if metadata["node_kind"] == "textgroup":
                self.text_groups[metadata["urn"]] = metadata
            elif metadata["node_kind"] == "work":
                self.works[metadata["urn"]] = metadata
                self.populate_versions(dirpath, metadata["versions"])

        return self.text_groups, self.works, self.versions


class Library:
    def __init__(self, text_groups, works, versions):
        self.text_groups = text_groups
        self.works = works
        self.versions = versions


class CTSImporter:
    """
    urn:cts:CTSNAMESPACE:WORK:PASSAGE
    https://cite-architecture.github.io/ctsurn_spec
    """

    CTS_URN_SCHEME = constants.CTS_URN_NODES[:-1]
    CTS_URN_SCHEME_EXEMPLAR = constants.CTS_URN_NODES
    INCLUDE_TEXTPARTS = False

    def get_text_group_metadata(self):
        text_group_urn = self.urn.up_to(self.urn.TEXTGROUP)
        metadata = self.library.text_groups[text_group_urn]
        name = metadata["name"][0]
        return dict(label=name["value"], lang=name["lang"])

    def get_work_metadata(self):
        work_urn = self.urn.up_to(self.urn.WORK)
        metadata = self.library.works[work_urn]
        return dict(lang=metadata["lang"], label=metadata["title"][0]["value"])

    def get_version_metadata(self):
        default = {
            # @@@ how much of the `metadata.json` do we
            # "pass through" via GraphQL vs
            # apply to particular node kinds in the heirarchy
            "citation_scheme": self.citation_scheme,
            "work_title": self.name,
            "first_passage_urn": self.version_data.get("first_passage_urn"),
            "default_toc_urn": self.version_data.get("default_toc_urn"),
        }
        # @@@ label
        default.update(
            dict(
                label=self.version_data["label"][0]["value"],
                description=self.version_data["description"][0]["value"],
                lang=self.version_data["lang"],
                kind=self.version_data["version_kind"],
            )
        )
        return default

    def __init__(self, library, version_data, nodes=dict()):
        self.library = library
        self.version_data = version_data
        self.nodes = nodes
        self.urn = URN(self.version_data["urn"].strip())
        self.work_urn = self.urn.up_to(self.urn.WORK)
        self.name = get_first_value_for_language(
            self.library.works[self.work_urn]["title"], "eng"
        )
        self.citation_scheme = self.version_data["citation_scheme"]
        self.metadata = self.get_version_metadata()
        self.idx_lookup = defaultdict(int)

        self.nodes_to_create = []
        self.node_last_child_lookup = defaultdict()

    @staticmethod
    def add_root(data):
        return Node.add_root(**data)

    @staticmethod
    def add_child(parent, data):
        return parent.add_child(**data)

    @staticmethod
    def check_depth(path):
        return len(path) > Node._meta.get_field("path").max_length

    @staticmethod
    def set_numchild(node):
        # @@@ experiment with F expressions
        # @@@ experiment with path__range queries
        node.numchild = Node.objects.filter(
            path__startswith=node.path, depth=node.depth + 1
        ).count()

    @staticmethod
    def get_parent_urn(idx, branch_data):
        return branch_data[idx - 1]["urn"] if idx else None

    def get_node_idx(self, kind):
        idx = self.idx_lookup[kind]
        self.idx_lookup[kind] += 1
        return idx

    def get_root_urn_scheme(self, node_urn):
        if node_urn.has_exemplar:
            return self.CTS_URN_SCHEME_EXEMPLAR
        return self.CTS_URN_SCHEME

    def get_urn_scheme(self, node_urn):
        return [*self.get_root_urn_scheme(node_urn), *self.citation_scheme]

    def get_partial_urn(self, kind, node_urn):
        scheme = self.get_root_urn_scheme(node_urn)
        kind_map = {kind: getattr(URN, kind.upper()) for kind in scheme}
        return node_urn.up_to(kind_map[kind])

    def add_child_bulk(self, parent, node_data):
        # @@@ bastardized version of `Node._inc_path`
        # https://github.com/django-treebeard/django-treebeard/blob/master/treebeard/mp_tree.py#L1121
        child_node = Node(**node_data)
        child_node.depth = parent.depth + 1

        last_child = self.node_last_child_lookup.get(parent.urn)
        if not last_child:
            # The node had no children, adding the first child.
            child_node.path = Node._get_path(parent.path, child_node.depth, 1)
            if self.check_depth(child_node.path):
                raise PathOverflow(
                    ugettext_noop(
                        "The new node is too deep in the tree, try"
                        " increasing the path.max_length property"
                        " and UPDATE your database"
                    )
                )
        else:
            # Adding the new child as the last one.
            child_node.path = last_child._inc_path()
        self.node_last_child_lookup[parent.urn] = child_node
        self.nodes_to_create.append(child_node)
        return child_node

    def use_bulk(self, node_data):
        return bool(node_data.get("rank"))

    def generate_node(self, idx, node_data, parent_urn):
        if idx == 0:
            return self.add_root(node_data)
        parent = self.nodes.get(parent_urn)
        if self.use_bulk(node_data):
            return self.add_child_bulk(parent, node_data)
        return self.add_child(parent, node_data)

    def destructure_urn(self, node_urn, tokens):
        node_data = []
        bad_urns = [
            "urn:cts:perslit:moulavi:",
            "urn:cts:perslit:salman:"
        ]
        if node_urn.up_to(node_urn.TEXTGROUP) in bad_urns:
            return node_data

        for kind in self.get_urn_scheme(node_urn):
            data = {"kind": kind}
            # @@@ duplicate; we might need a cts_ prefix for work, for example
            if kind not in self.citation_scheme or kind == "work" and not tokens:
                data.update({"urn": self.get_partial_urn(kind, node_urn)})
                if kind == "version":
                    data.update({"metadata": self.get_version_metadata()})
                elif kind == "work":
                    data.update({"metadata": self.get_work_metadata()})
                elif kind == "textgroup":
                    data.update({"metadata": self.get_text_group_metadata()})
            else:
                if not self.INCLUDE_TEXTPARTS:
                    continue

                ref_index = self.citation_scheme.index(kind)
                ref = ".".join(node_urn.passage_nodes[: ref_index + 1])
                urn = f"{node_urn.up_to(node_urn.NO_PASSAGE)}{ref}"
                data.update({"urn": urn, "ref": ref, "rank": ref_index + 1})
                if kind == self.citation_scheme[-1]:
                    data.update({"text_content": tokens})

            node_data.append(data)

        return node_data

    def generate_branch(self, line):
        if line:
            ref, tokens = line.strip().split(maxsplit=1)
        else:
            ref = ""
            tokens = ""
        node_urn = URN(f"{self.urn}{ref}")
        branch_data = self.destructure_urn(node_urn, tokens)
        for idx, node_data in enumerate(branch_data):
            node = self.nodes.get(node_data["urn"])
            if node is None:
                node_data.update({"idx": self.get_node_idx(node_data["kind"])})
                parent_urn = self.get_parent_urn(idx, branch_data)
                node = self.generate_node(idx, node_data, parent_urn)
                self.nodes[node_data["urn"]] = node

    def update_numchild_values(self):
        self.set_numchild(self.version_node)
        self.version_node.save()
        # @@@ `bulk_update` requires Django 2.2
        # we can skip this for now because we don't need to update text parts,
        # just versions.

        # to_update = [self.version_node]

        # # once `numchild` is set on version, we can get descendants
        # descendants = self.version_node.get_descendants()
        # max_depth = descendants.all().aggregate(max_depth=Max("depth"))["max_depth"]
        # for node in descendants.exclude(depth=max_depth):
        #     self.set_numchild(node)
        #     to_update.append(node)
        # Node.objects.bulk_update(to_update, ["numchild"], batch_size=500)

    def finalize(self):
        self.version_node = Node.objects.filter(urn=self.urn.absolute).first()
        if not self.version_node:
            print(f"Could not find a version matching {self.urn.absolute}")
            return 0
        Node.objects.bulk_create(self.nodes_to_create, batch_size=500)
        self.update_numchild_values()
        return self.version_node.get_descendant_count() + 1

    def apply(self):
        if self.INCLUDE_TEXTPARTS:
            full_content_path = self.library.versions[self.urn.absolute]["path"]
            with open(full_content_path, "r") as f:
                for line in f:
                    self.generate_branch(line)
        else:
            self.generate_branch("")

        count = self.finalize()
        print(f"{self.name}: {count} nodes.", file=sys.stderr)


def resolve_library():
    text_groups, works, versions = CTSCollectionResolver().resolved
    return Library(text_groups, works, versions)


def get_first_value_for_language(values, lang):
    for value in values:
        if value["lang"] == lang:
            return value["value"]
    # @@@ fallback to the last value
    return value["value"]

def import_versions():
    Node.objects.filter(kind="nid").delete()

    library = resolve_library()

    nodes = {}
    for _, version_data in library.versions.items():
        CTSImporter(library, version_data, nodes).apply()
    print(f"{Node.objects.count()} total nodes on the tree.", file=sys.stderr)
