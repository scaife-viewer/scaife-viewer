from functools import wraps

from django.views.decorators.http import condition


class ConditionMixin:

    def dispatch(self, request, *args, **kwargs):
        ckwargs = {}
        if hasattr(self, "get_etag"):
            ckwargs["etag_func"] = self.get_etag
        if hasattr(self, "get_last_modified"):
            ckwargs["last_modified_func"] = self.get_last_modified
        return condition(**ckwargs)(super().dispatch)(request, *args, **kwargs)


def cache_control(max_age=0, s_max_age=300):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            if response.get("Content-Type", "") == "application/json":
                # response is cachable
                # client and proxy caches must revalidate on every request
                # revalidation is cheap
                response["Cache-Control"] = f"public, must-revalidate, max-age={max_age}, s-maxage={s_max_age}, stale-while-revalidate, stale-if-error"
            return response
        return wrapper
    return decorator
