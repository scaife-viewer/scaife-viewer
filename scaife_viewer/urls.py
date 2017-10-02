from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

from .views import home, library, library_cts_resource, library_reader


urlpatterns = [
    url(r"^$", home, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r"^library/$", library, name="library"),
    url(r"^library/reader/(?P<urn>urn:[^/]+)/$", library_reader, name="library_reader"),
    url(r"^library/(?P<urn>urn:[^/]+)/", library_cts_resource, name="library_cts_resource"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
