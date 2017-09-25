from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

from .views import home, cts_resource, reader


urlpatterns = [
    url(r"^$", home, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r"^reader/(?P<urn>urn:[^/]+)/$", reader, name="reader"),
    url(r"(?P<urn>urn:[^/]+)/", cts_resource, name="cts_resource"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
