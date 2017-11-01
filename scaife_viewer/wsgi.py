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
    from .cts.text_inventory import TextInventory
    # calling this will prime the cache in the master process. each fork
    # will inherit it. to work call gunicorn with --preload
    TextInventory.load()


setup()
application = get_wsgi_application()
