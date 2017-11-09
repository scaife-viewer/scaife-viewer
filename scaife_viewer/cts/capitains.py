import logging
import os

from django.conf import settings

from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever

from .resolvers import LocalResolver


resolver = None
logger = logging.getLogger(__name__)


def api_resolver(endpoint) -> Resolver:
    return HttpCtsResolver(HttpCtsRetriever(endpoint))


def local_resolver(data_path: str) -> Resolver:
    resource = [
        os.path.join(data_path, entry)
        for entry in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, entry))
    ]
    return LocalResolver(resource, logger=logger)


def default_resolver() -> Resolver:
    global resolver
    if resolver is None:
        resolver_func = {
            "api": api_resolver,
            "local": local_resolver,
        }[settings.CTS_RESOLVER["type"]]
        resolver = resolver_func(**settings.CTS_RESOLVER["kwargs"])
    return resolver
