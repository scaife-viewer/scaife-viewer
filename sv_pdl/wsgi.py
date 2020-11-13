"""
WSGI config for sv_pdl project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


def setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sv_pdl.settings")
    from django.conf import settings

    from scaife_viewer.core import cts

    # calling this will prime the cache in the master process. each fork
    # will inherit it. gunicorn --preload is required for this to work.
    if settings.DEBUG is False:
        cts.TextInventory.load()
        print("Loaded text inventory")


def healthz(app):
    def healthz_wrapper(environ, start_response):
        if environ.get("PATH_INFO") == "/healthz/":
            start_response("200 OK", [("Content-Type", "text/plain")])
            return [b"ok"]
        return app(environ, start_response)
    return healthz_wrapper


setup()
application = healthz(get_wsgi_application())
