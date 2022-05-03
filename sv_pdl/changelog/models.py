from django.db import models


class ChangelogEntry(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    release_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "changelog entries"

    def __str__(self):
        return self.title

    def release_tag(self):
        return self.release_url.rsplit("/", maxsplit=1)[1]
