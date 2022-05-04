from django.contrib import admin

from .models import ChangelogEntry


@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "body", "release_url", "timestamp")
    list_filter = ("timestamp",)
