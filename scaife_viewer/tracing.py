import base64
import collections
import datetime
import json
import os
import threading
import time

from django.conf import settings

import opentracing
import opentracing.ext.tags as ext_tags
import wrapt
from basictracer import BasicTracer
from basictracer.recorder import SpanRecorder
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from opentracing import (
    Format,
    InvalidCarrierException,
    SpanContextCorruptedException
)


def to_timestamp(t):
    return datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class TracingState:

    _config = threading.local()

    @classmethod
    def activated(cls):
        return getattr(cls._config, "activated", False)

    @classmethod
    def set_config(cls, key, value):
        setattr(cls._config, key, value)


class Recorder(SpanRecorder):

    def __init__(self):
        self.mutex = threading.Lock()
        self.pending = collections.deque()
        self.disabled = False
        self.flush_thread = None
        self.setup_http()

    def setup_http(self):
        encoded_key = os.environ.get("GCP_TRACING_SERVICE_ACCOUNT")
        if not encoded_key:
            raise RuntimeError("missing GCP_TRACING_SERVICE_ACCOUNT")
        service_account_key = json.loads(base64.b64decode(encoded_key))
        self.project_id = service_account_key["project_id"]
        credentials = service_account.Credentials.from_service_account_info(service_account_key)
        scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/trace.append"])
        self.http = AuthorizedSession(scoped_credentials)

    def record_span(self, span):
        self.maybe_flush()
        s = {
            "spanId": str(span.context.span_id),
            "kind": {
                ext_tags.SPAN_KIND_RPC_CLIENT: 1,
                ext_tags.SPAN_KIND_RPC_SERVER: 2,
            }.get(span.tags.get(ext_tags.SPAN_KIND), 0),
            "name": span.operation_name,
            "startTime": to_timestamp(span.start_time),
            "endTime": to_timestamp(span.start_time + span.duration),
            "labels": {
                {
                    ext_tags.HTTP_METHOD: "trace.cloud.google.com/http/method",
                    ext_tags.HTTP_STATUS_CODE: "trace.cloud.google.com/http/status_code",
                    ext_tags.HTTP_URL: "trace.cloud.google.com/http/url",
                }.get(str(k), str(k)): str(v)
                for k, v in span.tags.items()
            },
        }
        if span.parent_id is not None:
            s["parentSpanId"] = str(span.parent_id)
        t = {
            "projectId": self.project_id,
            "traceId": "{:x}".format(span.context.trace_id) * 2,
            "spans": [s],
        }
        with self.mutex:
            self.pending.append(t)

    def maybe_flush(self):
        thread = self.flush_thread
        if (thread is not None and not thread.is_alive()) or thread is None:
            self.flush_thread = thread = threading.Thread(target=self.flusher, name="flusher")
            thread.daemon = True
            thread.start()

    def flusher(self):
        while not self.disabled:
            if self.pending:
                traces = list(self.pending)
                self.pending.clear()
                with self.mutex:
                    url = f"https://cloudtrace.googleapis.com/v1/projects/{self.project_id}/traces"
                    payload = {
                        "traces": traces,
                    }
                    headers = {
                        "Content-Type": "application/json",
                    }
                    r = self.http.patch(url, data=json.dumps(payload), headers=headers)
                    if not r.ok:
                        print(f"trace PUT failed status={r.status_code}")
            time.sleep(2.5)


class GCPTracer(BasicTracer):

    def __init__(self):
        recorder = None
        if settings.TRACING_ENABLED:
            recorder = Recorder()
        super(GCPTracer, self).__init__(recorder)
        self.register_required_propagators()


def parse_http_headers(request):
    prefix = "HTTP_"
    p_len = len(prefix)
    headers = {
        key[p_len:].replace("_", "-").lower(): value
        for key, value in request.META.items()
        if key.startswith(prefix)
    }
    return headers


class OpenTracingMiddleware:

    def __init__(self, get_response=None):
        self.tracer = GCPTracer()
        self.get_response = get_response

        install_requests_patch(self.tracer)

    def __call__(self, request):
        TracingState.set_config("activated", True)
        headers = parse_http_headers(request)
        tags = {
            ext_tags.SPAN_KIND: ext_tags.SPAN_KIND_RPC_SERVER,
            ext_tags.HTTP_URL: request.path,
            ext_tags.HTTP_METHOD: request.method,
        }
        span = None
        operation_name = request.path
        try:
            # check http headers to see if we should extract a parent span
            span_ctx = self.tracer.extract(Format.HTTP_HEADERS, carrier=headers)
            span = self.tracer.start_span(
                operation_name=operation_name,
                child_of=span_ctx,
                tags=tags,
            )
        except (InvalidCarrierException, SpanContextCorruptedException) as e:
            span = self.tracer.start_span(operation_name=operation_name, tags=tags)
        with span_in_context(span):
            response = self.get_response(request)
        span.set_tag(ext_tags.HTTP_STATUS_CODE, response.status_code)
        span.finish()
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        span = get_current_span()
        span.set_tag("django.view", view_func.__name__)

    def process_exception(self, request, exc):
        span = get_current_span()
        if span is not None:
            # span.set_tag(ext_tags.ERROR, str(exc))
            span.finish()


class RequestContext(object):

    __slots__ = ("span",)

    def __init__(self, span):
        self.span = span


class RequestContextManager:

    _state = threading.local()
    _state.context = None

    @classmethod
    def current_context(cls):
        return getattr(cls._state, "context", None)

    def __init__(self, context):
        if isinstance(context, opentracing.Span):
            self._context = RequestContext(span=context)
        else:
            self._context = context

    def __enter__(self):
        self._prev_context = self.__class__.current_context()
        self.__class__._state.context = self._context
        return self._context

    def __exit__(self, *_):
        self.__class__._state.context = self._prev_context
        self._prev_context = None
        return False


def get_current_span():
    context = RequestContextManager.current_context()
    return context.span if context else None


def span_in_context(span):
    context = RequestContext(span)
    return RequestContextManager(context)


def install_requests_patch(tracer):
    try:
        import requests.sessions
        import requests.adapters
    except ImportError:  # pragma: no cover
        return

    @wrapt.decorator
    def trace(wrapped, instance, args, kwargs):
        if TracingState.activated():
            span = tracer.start_span(
                operation_name="requests",
                child_of=get_current_span(),
            )
            with span:
                resp = wrapped(*args, **kwargs)
        else:
            resp = wrapped(*args, **kwargs)
        return resp

    requests.adapters.HTTPAdapter.send = trace(requests.adapters.HTTPAdapter.send)
