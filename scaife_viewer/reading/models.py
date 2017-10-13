from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from ..cts import Passage


class ReadingLog(models.Model):
    user = models.ForeignKey(User)
    urn = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def metadata(self):
        passage = Passage(self.urn)
        parents = passage.metadata.parents
        return {
            "textgroup_label": str(parents[1].get_label()),
            "work_label": str(parents[0].get_label()),
            "version_label": str(passage.metadata.get_label()),
            "reference": str(passage.reference),
            "lang": passage.lang,
        }

    @property
    def label(self):
        m = self.metadata
        return f"{m['textgroup_label']}, {m['work_label']} {m['reference']} ({m['lang']})"
