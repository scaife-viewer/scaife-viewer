from django.db.models import Max, Min, Q

import django_filters
from graphene import Boolean, Connection, Field, ObjectType, String, relay
from graphene.types import generic
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.utils import camelize

from scaife_viewer import cts

from .models import Node as TextPart
from .urn import URN
from .utils import get_chunker


def extract_version_urn_and_ref(value):
    dirty_version_urn, ref = value.rsplit(":", maxsplit=1)
    # Restore the trailing ":".
    version_urn = f"{dirty_version_urn}:"
    return version_urn, ref


def filter_via_ref_predicate(instance, queryset, predicate):
    # We need a sequential identifier to do the range unless there is something
    # else we can do with siblings / slicing within treebeard. Using `path`
    # might work too, but having `idx` also allows us to do simple integer math
    # as-needed.
    if queryset.exists():
        subquery = queryset.filter(predicate).aggregate(min=Min("idx"), max=Max("idx"))
        queryset = queryset.filter(idx__gte=subquery["min"], idx__lte=subquery["max"])
    return queryset


class LimitedConnectionField(DjangoFilterConnectionField):
    """
    Ensures that queries without `first` or `last` return up to
    `max_limit` results.
    """

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filtering_args,
        root,
        info,
        **resolver_kwargs,
    ):
        first = resolver_kwargs.get("first")
        last = resolver_kwargs.get("last")
        if not first and not last:
            resolver_kwargs["first"] = max_limit

        return super(LimitedConnectionField, cls).connection_resolver(
            resolver,
            connection,
            default_manager,
            max_limit,
            enforce_first_or_last,
            filterset_class,
            filtering_args,
            root,
            info,
            **resolver_kwargs,
        )


class PassageTextPartConnection(Connection):
    metadata = generic.GenericScalar()

    class Meta:
        abstract = True

    @staticmethod
    def generate_passage_urn(version, object_list):
        first = object_list[0]
        last = object_list[-1]

        if first == last:
            return first.get("urn")
        line_refs = [tp.get("ref") for tp in [first, last]]
        passage_ref = "-".join(line_refs)
        return f"{version.urn}{passage_ref}"

    def get_ancestor_metadata(self, version, obj):
        # @@@ this is currently the "first" ancestor
        # and we need to stop it at the version boundary for backwards
        # compatability with SV
        data = []
        if obj and obj.get_parent() != version:
            ancestor_urn = obj.urn.rsplit(".", maxsplit=1)[0]
            ancestor_ref = ancestor_urn.rsplit(":", maxsplit=1)[1]
            data.append(
                {
                    # @@@ proper name for this is ref or position?
                    "ref": ancestor_ref,
                    "urn": ancestor_urn,
                }
            )
        return data

    def get_sibling_metadata(self, version, all_queryset, start_idx, count):
        data = {}

        chunker = get_chunker(
            all_queryset, start_idx, count, queryset_values=["idx", "urn", "ref"]
        )
        previous_objects, next_objects = chunker.get_prev_next_boundaries()

        if previous_objects:
            data["previous"] = self.generate_passage_urn(version, previous_objects)

        if next_objects:
            data["next"] = self.generate_passage_urn(version, next_objects)
        return data

    def get_children_metadata(self, start_obj):
        data = []
        for tp in start_obj.get_children().values("ref", "urn"):
            # @@@ denorm lsb
            lsb = tp["ref"].rsplit(".", maxsplit=1)[-1]
            data.append(
                {
                    # @@@ proper name is lsb or position
                    "lsb": lsb,
                    "urn": tp.get("urn"),
                }
            )
        return data

    def resolve_metadata(self, info, *args, **kwargs):
        # @@@ resolve metadata.siblings|ancestors|children individually
        passage_dict = info.context.passage
        if not passage_dict:
            return

        urn = passage_dict["urn"]
        version = passage_dict["version"]

        refs = urn.rsplit(":", maxsplit=1)[1].split("-")
        first_ref = refs[0]
        last_ref = refs[-1]
        if first_ref == last_ref:
            start_obj = end_obj = version.get_descendants().get(ref=first_ref)
        else:
            start_obj = version.get_descendants().get(ref=first_ref)
            end_obj = version.get_descendants().get(ref=last_ref)

        data = {}
        siblings_qs = start_obj.get_siblings()
        start_idx = start_obj.idx
        chunk_length = end_obj.idx - start_obj.idx + 1
        data["ancestors"] = self.get_ancestor_metadata(version, start_obj)
        data["siblings"] = self.get_sibling_metadata(
            version, siblings_qs, start_idx, chunk_length
        )
        data["children"] = self.get_children_metadata(start_obj)
        return camelize(data)


class TextPartFilterSet(django_filters.FilterSet):
    reference = django_filters.CharFilter(method="reference_filter")

    def reference_filter(self, queryset, name, value):
        version_urn, ref = extract_version_urn_and_ref(value)
        start, end = ref.split("-")
        refs = [start]
        if end:
            refs.append(end)
        predicate = Q(ref__in=refs)
        queryset = queryset.filter(
            urn__startswith=version_urn, depth=len(start.split(".")) + 1
        )
        return filter_via_ref_predicate(self, queryset, predicate)

    class Meta:
        model = TextPart
        fields = {
            "urn": ["exact", "startswith"],
            "ref": ["exact", "startswith"],
            "depth": ["exact", "lt", "gt"],
            "rank": ["exact", "lt", "gt"],
            "kind": ["exact"],
            "idx": ["exact"],
        }


# @@@ we might share parts of this reference filter to TextPartFilterSet
class PassageTextPartFilterSet(django_filters.FilterSet):
    reference = django_filters.CharFilter(method="reference_filter")

    class Meta:
        model = TextPart
        fields = []

    def _add_passage_to_context(self, reference):
        # @@@ instance.request is an alias for info.context and used to store
        # context data across filtersets
        self.request.passage = dict(urn=reference)

        version_urn, ref = extract_version_urn_and_ref(reference)
        try:
            version = TextPart.objects.get(urn=version_urn)
        except TextPart.DoesNotExist:
            raise Exception(f"{version_urn} was not found.")

        self.request.passage["version"] = version

    def _build_predicate(self, queryset, ref, max_rank):
        predicate = Q()
        if not ref:
            # @@@ get all the text parts in the work; do we want to support this
            # or should we just return the first text part?
            start = queryset.first().ref
            end = queryset.last().ref
        else:
            try:
                start, end = ref.split("-")
            except ValueError:
                start = end = ref

        # @@@ still need to validate reference based on the depth
        # start_book, start_line = instance._resolve_ref(start)
        # end_book, end_line = instance._resolve_ref(end)
        # the validation might be done through treebeard; for now
        # going to avoid the queries at this time
        if start:
            if len(start.split(".")) == max_rank:
                condition = Q(ref=start)
            else:
                condition = Q(ref__istartswith=f"{start}.")
            predicate.add(condition, Q.OR)
        if end:
            if len(end.split(".")) == max_rank:
                condition = Q(ref=end)
            else:
                condition = Q(ref__istartswith=f"{end}.")
            predicate.add(condition, Q.OR)
        if not start or not end:
            raise ValueError(f"Invalid reference: {ref}")

        return predicate

    def reference_filter(self, queryset, name, value):
        self._add_passage_to_context(value)

        version = self.request.passage["version"]
        citation_scheme = version.metadata["citation_scheme"]
        max_depth = version.get_descendants().last().depth
        max_rank = len(citation_scheme)

        queryset = version.get_descendants().filter(depth=max_depth)
        _, ref = value.rsplit(":", maxsplit=1)
        predicate = self._build_predicate(queryset, ref, max_rank)
        return filter_via_ref_predicate(self, queryset, predicate)


class AbstractTextPartNode(DjangoObjectType):
    label = String()
    name = String()
    metadata = generic.GenericScalar()

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **meta_options):
        meta_options.update(
            {
                "model": TextPart,
                "interfaces": (relay.Node,),
                "filterset_class": TextPartFilterSet,
            }
        )
        super().__init_subclass_with_meta__(**meta_options)

    def resolve_metadata(obj, *args, **kwargs):
        return camelize(obj.metadata)


class VersionNode(AbstractTextPartNode):
    access = Boolean()
    description = String()
    label = String()
    lang = String()
    human_lang = String()
    kind = String()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(kind="version").order_by("pk")

    def resolve_access(obj, *args, **kwargs):
        # @@@ actually check access
        return True

    def resolve_human_lang(obj, *args, **kwargs):
        lang = obj.metadata["lang"]
        # @@@ make the language map decoupled from cts
        return cts.constants.LANGAUGE_MAP.get(lang, lang)

    def resolve_lang(obj, *args, **kwargs):
        return obj.metadata["lang"]

    def resolve_description(obj, *args, **kwargs):
        # @@@ consider a direct field or faster mapping
        return obj.metadata["description"]

    def resolve_kind(obj, *args, **kwargs):
        # @@@ consider a direct field or faster mapping
        return obj.metadata["kind"]

    def resolve_label(obj, *args, **kwargs):
        # @@@ consider a direct field or faster mapping
        return obj.metadata["label"]

    def resolve_metadata(obj, *args, **kwargs):
        metadata = obj.metadata
        # @@@ revisit first_passage_urn and work metadata
        # metadata.update(
        #     {"work_urn": URN(metadata["first_passage_urn"]).up_to(URN.WORK)}
        # )
        return camelize(metadata)


class WorkNode(AbstractTextPartNode):
    # @@@ apply a subfilter here?
    versions = LimitedConnectionField(lambda: VersionNode)
    label = String()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(kind="work").order_by("pk")

    def resolve_label(obj, *args, **kwargs):
        # @@@ consider a direct field or faster mapping
        return obj.metadata["label"]

    def resolve_metadata(obj, *args, **kwargs):
        metadata = obj.metadata
        return camelize(metadata)


class TextGroupNode(AbstractTextPartNode):
    # @@@ work or version relations

    label = String()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(kind="textgroup").order_by("urn")

    def resolve_label(obj, *args, **kwargs):
        # @@@ consider a direct field or faster mapping
        return obj.metadata["label"]

    def resolve_metadata(obj, *args, **kwargs):
        metadata = obj.metadata
        return camelize(metadata)


class TextPartNode(AbstractTextPartNode):
    pass


class PassageTextPartNode(DjangoObjectType):
    label = String()

    class Meta:
        model = TextPart
        interfaces = (relay.Node,)
        connection_class = PassageTextPartConnection
        filterset_class = PassageTextPartFilterSet


class TreeNode(ObjectType):
    tree = generic.GenericScalar()

    def resolve_tree(obj, info, **kwargs):
        return obj


class Query(ObjectType):
    text_group = relay.Node.Field(TextGroupNode)
    text_groups = LimitedConnectionField(TextGroupNode)

    work = relay.Node.Field(WorkNode)
    works = LimitedConnectionField(WorkNode)

    version = relay.Node.Field(VersionNode)
    versions = LimitedConnectionField(VersionNode)

    text_part = relay.Node.Field(TextPartNode)
    text_parts = LimitedConnectionField(TextPartNode)

    # No passage_text_part endpoint available here like the others because we
    # will only support querying by reference.
    passage_text_parts = LimitedConnectionField(PassageTextPartNode)

    tree = Field(TreeNode, urn=String(required=True), up_to=String(required=False))

    def resolve_tree(obj, info, urn, **kwargs):
        return TextPart.dump_tree(
            root=TextPart.objects.get(urn=urn), up_to=kwargs.get("up_to")
        )
