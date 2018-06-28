from importlib import import_module

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):

    name = "scaife_viewer"

    def ready(self):
        import_module("scaife_viewer.receivers")
