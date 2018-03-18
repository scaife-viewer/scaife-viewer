from django.conf.urls import url

from . import views

urlpatterns = [

    url(r"^$",
        views.ReadingListsView.as_view(), name="reading_lists"),
    url(r"^owner/(?P<user_pk>\d+)/$",
        views.ReadingListsView.as_view(), name="user_reading_lists"),
    url(r"^subscriptions/owner/(?P<user_pk>\d+)/$",
        views.ReadingListsSubscriptionsView.as_view(), name="reading_list_subscriptions"),

    url(r"^(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListDetailView.as_view(), name="reading_list"),

    url(r"^create/$",
        views.ReadingListCreateView.as_view(), name="reading_list_create"),
    url(r"^update/(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListUpdateView.as_view(), name="reading_list_update"),
    url(r"^delete/(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListDeleteView.as_view(), name="reading_list_delete"),

    url(r"^clone/(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListCloneView.as_view(), name="reading_list_clone"),
    url(r"^subscribe/(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListSubscribeView.as_view(), name="reading_list_subscribe"),
    url(r"^unsubscribe/(?P<secret_key>[0-9a-f-]+)/$",
        views.ReadingListSubscribeView.as_view(), name="reading_list_unsubscribe"),

    url(r"^logs/$", views.logs, name="reading_logs"),
]
