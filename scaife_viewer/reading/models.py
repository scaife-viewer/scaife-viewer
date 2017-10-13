from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class ReadingLog(models.Model):
    user = models.ForeignKey(User)
    urn = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)
