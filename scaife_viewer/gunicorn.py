from .cts.text_inventory import TextInventory


def when_ready(server):
    # calling this will prime the cache in the master process. each fork
    # will inherit it. to work call gunicorn with --preload
    TextInventory.load()
