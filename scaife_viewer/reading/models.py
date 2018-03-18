from .. import cts

import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.utils import NestedObjects
from django.db import connection, models, IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property


class AuditedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CloneableModel(models.Model):
    class Meta:
        abstract = True

    def _build_graph(self):
        graph = {}
        for key in self.related_models:
            pks = [item.pk for item in self.collector.data[key]]
            items = [item for item in self.collector.data[key]]
            graph.update({
                key: dict(zip(pks, items))
            })
        return graph

    def duplicate(self, owner):  # noqa
        root_obj = self._meta.model.objects.create(
            owner=owner,
            title=self.title,
            description=self.description,
            secret_key=uuid.uuid4(),
            cloned_from=self
        )
        self.collector = NestedObjects(using="default")
        self.collector.collect([self])
        self.collector.sort()
        self.related_models = self.collector.data.keys()
        graph = self._build_graph()

        for cls, instances in graph.items():
            if issubclass(cls, BaseListEntry):
                for _, obj in instances.items():
                    obj.id = None
                    obj.pk = None
                    obj.save()
                    root_obj.entries.add(obj)

        return root_obj


class BaseList(models.Model):
    owner = models.ForeignKey(
        getattr(settings, "AUTH_USER_MODEL", "auth.User"),
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    cloned_from = models.ForeignKey(
        "self", null=True, editable=False, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    secret_key = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.title} - {self.secret_key}"


class BaseListEntry(models.Model):
    note = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseSubscription(models.Model):
    subscriber = models.ForeignKey(
        getattr(settings, "AUTH_USER_MODEL", "auth.User"),
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._meta.model.objects.filter(
            resource_list=self.resource_list,
            subscriber=self.subscriber
        ).exists():
            raise IntegrityError("Duplicate subscription.")
        else:
            super().save(*args, **kwargs)


class ReadingList(AuditedModel, CloneableModel, BaseList):
    class Meta:
        verbose_name = "reading list"

    def get_absolute_url(self):
        return reverse("reading_list", kwargs={"secret_key": self.secret_key})


class ReadingListEntry(AuditedModel, BaseListEntry):
    cts_urn = models.CharField(max_length=250)
    resource_list = models.ForeignKey(
        "reading.ReadingList", related_name="entries"
    )

    class Meta:
        verbose_name = "reading list entry"
        verbose_name_plural = "reading list entries"
        order_with_respect_to = "resource_list"

    def __str__(self):
        return self.cts_urn

    @cached_property
    def text_edition(self):
        try:
            return TextEdition.objects.get(cts_urn=self.cts_urn)
        except TextEdition.DoesNotExist:
            cts_urn = ":".join(self.cts_urn.split(":")[:-1])
            return TextEdition.objects.get(cts_urn=cts_urn)


class ReadingListSubscription(AuditedModel, BaseSubscription):
    resource_list = models.ForeignKey(
        "reading.ReadingList", related_name="subscriptions"
    )

    class Meta:
        verbose_name = "reading list subscription"
        verbose_name_plural = "reading list subscriptions"


class ReadingLog(models.Model):
    user = models.ForeignKey(User)
    urn = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def metadata(self):
        return metadata(self.urn)


def metadata(urn):
    passage = cts.passage(urn)
    parents = list(passage.text.ancestors())
    return {
        "textgroup_label": str(parents[1].label),
        "work_label": str(parents[0].label),
        "version_label": str(passage.text.label),
        "reference": str(passage.reference).replace("-", "–"),
        "lang": passage.text.lang,
    }


def recent(user, limit=5):
    with connection.cursor() as cursor:
        sql = "SELECT urn, MAX(timestamp) AS timestamp FROM reading_readinglog WHERE user_id = %s GROUP BY urn ORDER BY timestamp DESC LIMIT %s"
        cursor.execute(sql, [user.pk, limit])

        return [
            {
                "metadata": metadata(row[0]),
                "urn": row[0],
                "timestamp": row[1],
            }
            for row in cursor.fetchall()
        ]
