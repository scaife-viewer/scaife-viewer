from django.utils.functional import cached_property

from .models import Node


class URN:
    """
    Provides a subset of functionality from `MyCapytain.common.reference.URN`.
    """

    NID = 0
    NAMESPACE = 1
    TEXTGROUP = 2
    WORK = 3
    VERSION = 4
    EXEMPLAR = 5
    NO_PASSAGE = 6
    WORK_COMPONENT_LABELS = {
        TEXTGROUP: "textgroup",
        WORK: "work",
        VERSION: "version",
        EXEMPLAR: "exemplar",
    }

    def __str__(self):
        return self.urn

    def __init__(self, urn):
        self.urn = urn
        self.parsed = self.parse_urn(urn)

    def parse_urn(self, urn):
        parsed = {}
        for v in self.WORK_COMPONENT_LABELS.values():
            parsed[v] = None

        components = urn.split(":")
        try:
            (
                nid,
                protocol,
                namespace_component,
                work_component,
                passage_component,
            ) = components[:5]
        except ValueError:
            raise ValueError(f"Invalid URN: {urn}")
        work_components = work_component.split(".")
        parsed.update(
            {
                "nid": nid,
                "protocol": protocol,
                "namespace": namespace_component,
                "ref": passage_component,
            }
        )
        for constant, value in enumerate(work_components, 2):
            key = self.WORK_COMPONENT_LABELS[constant]
            parsed[key] = value
        return parsed

    @cached_property
    def node(self):
        if self.is_range:
            # TODO: Return entire range of Nodes?
            raise NotImplementedError("A range URN implies multiple nodes.")
        return Node.objects.get(urn=self.absolute)

    @property
    def absolute(self):
        return self.urn

    @property
    def is_range(self):
        return self.passage is not None and "-" in self.passage

    @property
    def has_exemplar(self):
        return self.parsed["exemplar"] is not None

    @property
    def passage(self):
        return self.parsed["ref"]

    @property
    def passage_nodes(self):
        return self.passage.split(".")

    @property
    def to_nid(self):
        return ":".join([self.parsed["nid"], self.parsed["protocol"]])

    @property
    def to_namespace(self):
        return ":".join([self.to_nid, self.parsed["namespace"]])

    @property
    def to_textgroup(self):
        return ":".join([self.to_namespace, self.parsed["textgroup"]])

    @property
    def to_work(self):
        return ".".join([self.to_textgroup, self.parsed["work"]])

    @property
    def to_version(self):
        return ".".join([self.to_work, self.parsed["version"]])

    @property
    def to_exemplar(self):
        return ".".join([self.to_version, self.parsed["exemplar"]])

    @property
    def to_no_passage(self):
        if self.parsed["ref"]:
            return self.urn.rsplit(":", maxsplit=1)[0]
        return self.urn

    def up_to(self, key):
        if key == self.NO_PASSAGE:
            label = "no_passage"
        elif key == self.NID:
            label = "nid"
        elif key == self.NAMESPACE:
            label = "namespace"
        else:
            label = self.WORK_COMPONENT_LABELS.get(key, None)
        if label is None:
            raise KeyError(f"Provided key is not recognized: {key}")

        attr_name = f"to_{label}"
        try:
            value = getattr(self, attr_name)
        except TypeError:
            raise ValueError(f"URN has no component: {label}")

        return f"{value}:"
