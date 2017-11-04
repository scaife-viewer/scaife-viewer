import os

from django.conf import settings

from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


resolver = None


def api_resolver(endpoint) -> Resolver:
    return HttpCtsResolver(HttpCtsRetriever(endpoint))


def local_resolver(data_path: str) -> Resolver:
    return CtsCapitainsLocalResolver([
        os.path.join(data_path, entry)
        for entry in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, entry))
    ])


def default_resolver() -> Resolver:
    global resolver
    if resolver is None:
        resolver_func = {
            "api": api_resolver,
            "local": local_resolver,
        }[settings.CTS_RESOLVER["type"]]
        resolver = resolver_func(**settings.CTS_RESOLVER["kwargs"])
    return resolver
