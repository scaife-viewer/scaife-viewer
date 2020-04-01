from django.conf import settings
from django.db.models import Max, Min
from django.utils.functional import cached_property


class BaseSiblingChunker:
    def __init__(self, queryset, start_idx, chunk_length, queryset_values=None):
        if queryset_values is None:
            queryset_values = ["idx"]

        self.queryset = queryset
        self.start_idx = start_idx
        self.chunk_length = chunk_length
        self.queryset_values = queryset_values

    def get_queryset(self):
        return self.queryset.values(*self.queryset_values)


class InMemorySiblingChunker(BaseSiblingChunker):
    """
    @@@ Tests showed that doing this chunking in-memory
    was faster up to ~7500 lines
    e.g. urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:9.24-12.389
    """

    @cached_property
    def object_list(self):
        previous_idx = self.start_idx - self.chunk_length
        next_idx = self.start_idx + (self.chunk_length * 2) - 1
        queryset = self.get_queryset()
        return list(queryset.filter(idx__gte=previous_idx, idx__lte=next_idx))

    def get_pivot_index(self):
        for pos, obj in enumerate(self.object_list):
            if obj.get("idx") == self.start_idx:
                return pos
        raise IndexError(f"Could not find idx value of {self.start_idx} in object_list")

    @cached_property
    def previous_boundary_objs(self):
        objs = self.object_list[: self.pivot_index]
        if objs:
            return [objs[0], objs[-1]]
        return []

    @cached_property
    def next_boundary_objs(self):
        objs = self.object_list[self.pivot_index + self.chunk_length :]
        if objs:
            return [objs[0], objs[-1]]
        return []

    def get_prev_next_boundaries(self):
        self.pivot_index = self.get_pivot_index()
        return self.previous_boundary_objs, self.next_boundary_objs


class SQLSiblingChunker(BaseSiblingChunker):
    """
    @@@ Tests showed that doing this chunking via SQL
    was faster when > 7500 lines
    """

    @cached_property
    def previous_boundary_objs(self):
        queryset = self.get_queryset()
        previous_queryset = queryset.order_by("-idx").filter(idx__lt=self.start_idx)[
            : self.chunk_length
        ]
        subquery = previous_queryset.aggregate(min=Min("idx"), max=Max("idx"))
        return list(queryset.filter(idx__in=[subquery["min"], subquery["max"]]))

    @cached_property
    def next_boundary_objs(self):
        queryset = self.get_queryset()
        next_queryset = queryset.order_by("idx").filter(idx__gte=self.start_idx)[
            self.chunk_length : self.chunk_length * 2
        ]
        subquery = next_queryset.aggregate(min=Min("idx"), max=Max("idx"))
        return list(queryset.filter(idx__in=[subquery["min"], subquery["max"]]))

    def get_prev_next_boundaries(self):
        return self.previous_boundary_objs, self.next_boundary_objs


def get_chunker(queryset, start_idx, chunk_length, **kwargs):
    if chunk_length < settings.ATLAS_CONFIG["IN_MEMORY_PASSAGE_CHUNK_MAX"]:
        return InMemorySiblingChunker(queryset, start_idx, chunk_length, **kwargs)
    return SQLSiblingChunker(queryset, start_idx, chunk_length, **kwargs)
