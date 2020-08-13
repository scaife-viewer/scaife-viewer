from django.urls import path

from .views import logs


urlpatterns = [
    path("logs/", logs, name="reading_logs"),
]
