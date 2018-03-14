from django.conf.urls import url

from .views import logs


urlpatterns = [
    url(r"^logs/$", logs, name="reading_logs"),
]
