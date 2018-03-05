from importlib import import_module

from django.apps import AppConfig as BaseAppConfig
from opencensus.trace import config_integration


class AppConfig(BaseAppConfig):

    name = "scaife_viewer"

    def ready(self):
        config_integration.trace_integrations([
            "postgresql",
            "requests",
        ])
        import_module("scaife_viewer.receivers")
