from django.conf import settings

from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


retriever = HttpCtsRetriever(settings.CTS_API_ENDPOINT)
resolver = HttpCtsResolver(retriever)
