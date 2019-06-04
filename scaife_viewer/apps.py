from importlib import import_module

from django.apps import AppConfig as BaseAppConfig
from django.conf import settings


class AppConfig(BaseAppConfig):

    name = "scaife_viewer"

    def ready(self):
        import_module("scaife_viewer.receivers")

        if settings.DEBUG is False:
            # calling this will prime the cache in the master process. each fork
            # will inherit it. gunicorn --preload is required for this to work.
            precomputed = import_module("scaife_viewer.precomputed")
            precomputed.library_view_json()
            print("Precomputed library view JSON")
