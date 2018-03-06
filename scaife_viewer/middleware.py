from functools import lru_cache
import copy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.core.handlers.exception import convert_exception_to_response
from django.urls import get_resolver
from django.utils.module_loading import import_string


class PerRequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.mws = {}
        for key in settings.PER_REQUEST_MIDDLEWARE.keys():
            self.load_middleware(key)

    def load_middleware(self, key):
        view_mw, template_response_mw, exception_mw = [], [], []
        MIDDLEWARE = settings.PER_REQUEST_MIDDLEWARE[key]
        handler = copy.deepcopy(self.get_response)
        for mw_path in reversed(MIDDLEWARE):
            try:
                mw_instance = import_string(mw_path)(handler)
            except MiddlewareNotUsed:
                continue
            if mw_instance is None:
                raise ImproperlyConfigured(f"Middleware factory {mw_path} returned None.")
            if hasattr(mw_instance, "process_view"):
                view_mw.insert(0, mw_instance.process_view)
            if hasattr(mw_instance, "process_template_response"):
                template_response_mw.append(mw_instance.process_template_response)
            if hasattr(mw_instance, "process_exception"):
                exception_mw.append(mw_instance.process_exception)
            handler = convert_exception_to_response(mw_instance)
        self.mws[(key, None)] = handler
        self.mws[(key, "view")] = view_mw
        self.mws[(key, "template_response")] = template_response_mw
        self.mws[(key, "exception")] = exception_mw

    @lru_cache(None)
    def resolve_key(self, path):
        resolver = get_resolver()
        match = resolver.resolve(path)
        if "api" in match.namespaces:
            return "api"
        return "default"

    def __call__(self, request):
        handler = self.mws[(self.resolve_key(request.path_info), None)]
        response = handler(request)
        if response is not None:
            return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        for mw_method in self.mws[(self.resolve_key(request.path_info), "view")]:
            response = mw_method(request, callback, callback_args, callback_kwargs)
            if response is not None:
                return response

    def process_template_response(self, request, response):
        for mw_method in self.mws[(self.resolve_key(request.path_info), "template_response")]:
            response = mw_method(request, response)
            if response is not None:
                return response

    def process_exception(self, request, e):
        for mw_method in self.mws[(self.resolve_key(request.path_info), "exception")]:
            response = mw_method(request, e)
            if response:
                return response
