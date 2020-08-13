from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from django.contrib import admin

from scaife_viewer.core.views import (
    LibraryCollectionVectorView,
    LibraryCollectionView,
    LibraryInfoView,
    LibraryPassageView,
    LibraryView,
    Reader,
    library_text_redirect,
    morpheus,
    search,
    search_json
)

from .views import (
    home,
    about,
    app,
    profile,
)


api_patterns = (
    [
        path("library/json/", LibraryView.as_view(format="json"), name="library"),
        path("library/json/info", LibraryInfoView.as_view(), name="library_info"),
        path("library/vector/<str:urn>/", LibraryCollectionVectorView.as_view(), name="library_collection_vector"),
        path("library/passage/<str:urn>/json/", LibraryPassageView.as_view(format="json"), name="library_passage"),
        path("library/passage/<str:urn>/text/", LibraryPassageView.as_view(format="text"), name="library_passage_text"),
        path("library/passage/<str:urn>/xml/", LibraryPassageView.as_view(format="xml"), name="library_passage_xml"),
        path("library/<str:urn>/json/", LibraryCollectionView.as_view(format="json"), name="library_collection"),
        path("search/json/", search_json, name="search"),
        path("morpheus/", morpheus, name="morpheus"),
    ],
    "api",
)

site_patterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("profile/", profile, name="profile"),
    path("search/", search, name="search"),
    path("reading/", include("sv_pdl.reading.urls")),
    path("openid/", include("oidc_provider.urls", namespace="oidc_provider")),
    path(".well-known/", include("letsencrypt.urls")),
]

scaife_viewer_patterns = [
    path("", include(api_patterns)),
    path("library/", LibraryView.as_view(format="html"), name="library"),
    path("library/<str:urn>/", LibraryCollectionView.as_view(format="html"), name="library_collection"),
    path("library/<str:urn>/redirect/", library_text_redirect, name="library_text_redirect"),
    path("reader/<str:urn>/", Reader.as_view(), name="reader"),

]

urlpatterns = site_patterns + scaife_viewer_patterns + [
    path("<path:path>/", app, name="app"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
