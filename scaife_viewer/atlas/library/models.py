import json

from django.conf import settings
from django.core import serializers
from django.db import models

# @@@ https://code.djangoproject.com/ticket/12990
from django_extensions.db.fields.json import JSONField
from graphene_django.utils import camelize
from treebeard.mp_tree import MP_Node

from .. import constants

# @@@ https://docs.djangoproject.com/en/3.0/topics/db/multi-db/
class Node(MP_Node):
    # @@@ used to pivot siblings; may be possible if we hook into path field
    idx = models.IntegerField(help_text="0-based index", blank=True, null=True)
    # @@@ if we expose kind, can access some GraphQL enumerations
    kind = models.CharField(max_length=255)
    urn = models.CharField(max_length=255, unique=True)
    ref = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    metadata = JSONField(default=dict, blank=True, null=True)

    alphabet = settings.ATLAS_CONFIG["NODE_ALPHABET"]

    def __str__(self):
        return f"{self.kind}: {self.urn}"

    @property
    def name(self):
        return self.metadata.get("work_title")

    @classmethod
    def dump_tree(cls, root=None, up_to=None, to_camel=True):
        """Dump a tree or subtree for serialization rendering all
        fieldnames as camelCase by default.

        Extension of django-treebeard.treebeard.mp_tree `dump_bulk` for
        finer-grained control over the initial queryset and resulting value.
        """
        if up_to and up_to not in constants.CTS_URN_NODES:
            raise ValueError(f"Invalid CTS node identifier for: {up_to}")

        qs = cls._get_serializable_model().get_tree(parent=root)
        if up_to:
            depth = constants.CTS_URN_DEPTHS[up_to]
            qs = qs.exclude(depth__gt=depth)

        tree, index = [], {}
        for pyobj in serializers.serialize("python", qs):
            fields = pyobj["fields"]
            path = fields["path"]
            depth = int(len(path) / cls.steplen)
            del fields["depth"]
            del fields["path"]
            del fields["numchild"]

            metadata = json.loads(fields["metadata"])
            if to_camel:
                fields = camelize(fields)
                metadata = camelize(metadata)
            fields.update({"metadata": metadata})

            newobj = {"data": fields}

            if (not root and depth == 1) or (root and len(path) == len(root.path)):
                tree.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = index[parentpath]
                if "children" not in parentobj:
                    parentobj["children"] = []
                parentobj["children"].append(newobj)
            index[path] = newobj
        return tree
