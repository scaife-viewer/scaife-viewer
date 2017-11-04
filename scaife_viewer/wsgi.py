"""
WSGI config for scaife_viewer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


def setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scaife_viewer.settings")
    from . import cts
    # calling this will prime the cache in the master process. each fork
    # will inherit it. gunicorn --preload is required for this to work.
    cts.TextInventory.load()
    print("Loaded text inventory")


setup()
application = get_wsgi_application()
