from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import (
    LibraryCollectionVectorView,
    LibraryCollectionView,
    LibraryPassageView,
    LibraryView,
    home,
    library_text_redirect,
    morpheus,
    profile,
    reader,
    search,
    search_json
)

api_patterns = (
    [
        url(r"^library/json/$", LibraryView.as_view(format="json"), name="library"),
        url(r"^library/vector/(?P<urn>[^/]+)/$", LibraryCollectionVectorView.as_view(), name="library_collection_vector"),
        url(r"^library/passage/(?P<urn>[^/]+)/json/", LibraryPassageView.as_view(format="json"), name="library_passage"),
        url(r"^library/passage/(?P<urn>[^/]+)/text/", LibraryPassageView.as_view(format="text"), name="library_passage_text"),
        url(r"^library/(?P<urn>[^/]+)/json/$", LibraryCollectionView.as_view(format="json"), name="library_collection"),
        url(r"^search/json/$", search_json, name="search"),
        url(r"^morpheus/", morpheus, name="morpheus"),
    ],
    "api",
)

urlpatterns = [
    url(r"^$", home, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r"", include(api_patterns)),
    url(r"^library/$", LibraryView.as_view(format="html"), name="library"),
    url(r"^library/(?P<urn>[^/]+)/$", LibraryCollectionView.as_view(format="html"), name="library_collection"),
    url(r"^library/(?P<urn>[^/]+)/redirect/$", library_text_redirect, name="library_text_redirect"),
    url(r"^reader/(?P<urn>urn:[^/]+)/$", reader, name="reader"),
    url(r"^profile/$", profile, name="profile"),
    url(r"^search/$", search, name="search"),
    url(r"^reading/", include("scaife_viewer.reading.urls")),
    url(r"^openid/", include("oidc_provider.urls", namespace="oidc_provider")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
