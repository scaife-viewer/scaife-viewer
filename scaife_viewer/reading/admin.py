from django.contrib import admin

from . import models


class ReadlingListEntryInline(admin.StackedInline):
    fields = ["cts_urn", "note"]
    model = models.ReadingListEntry
    extra = 1


@admin.register(models.ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    inlines = (ReadlingListEntryInline,)


@admin.register(models.ReadingListEntry)
class ReadingEntryListAdmin(admin.ModelAdmin):
    fields = ["cts_urn", "resource_list", "note"]


@admin.register(models.ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "urn", "timestamp"]
