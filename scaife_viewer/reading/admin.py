from django.contrib import admin

from .models import ReadingLog


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "urn", "timestamp"]
