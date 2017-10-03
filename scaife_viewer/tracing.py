import base64
import collections
import datetime
import json
import os
import time
import threading

import opentracing.ext.tags as ext_tags

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from basictracer import BasicTracer
from basictracer.binary_propagator import BinaryPropagator
from basictracer.text_propagator import TextPropagator
from basictracer.recorder import SpanRecorder
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from opentracing import (
    Format,
    InvalidCarrierException,
    SpanContextCorruptedException,
)


def to_timestamp(t):
    return datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


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
                    ext_tags.PEER_HOSTNAME: "trace.cloud.google.com/http/host",
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


class NoOpRecorder(SpanRecorder):

    def record_span(self, span):
        pass


class GCPTracer(BasicTracer):

    def __init__(self):
        if settings.TRACING_ACTIVATED:
            recorder = Recorder()
        else:
            recorder = NoOpRecorder()
        super(GCPTracer, self).__init__(recorder)
        self.register_propagator(Format.TEXT_MAP, TextPropagator())
        self.register_propagator(Format.HTTP_HEADERS, TextPropagator())
        self.register_propagator(Format.BINARY, BinaryPropagator())


class DjangoTracer(object):

    def __init__(self, tracer):
        self._tracer = tracer
        self._current_spans = {}

    def get_span(self, request):
        return self._current_spans.get(request, None)

    def _apply_tracing(self, request, view_func, attributes):
        carrier = {}
        for k, v in request.META.items():
            k = k.lower().replace("_", "-")
            if k.startswith("http-"):
                k = k[5:]
            carrier[k] = v
        tags = {
            ext_tags.SPAN_KIND: ext_tags.SPAN_KIND_RPC_SERVER,
            ext_tags.HTTP_URL: request.path,
            ext_tags.HTTP_METHOD: request.method,
        }
        span = None
        operation_name = f"view:{view_func.__name__}"
        span_ctx = self._tracer.extract(Format.HTTP_HEADERS, carrier=carrier)
        span = self._tracer.start_span(
            operation_name=operation_name,
            child_of=span_ctx,
            tags=tags,
        )
        self._current_spans[request] = span
        return span

    def _finish_tracing(self, request):
        span = self._current_spans.pop(request, None)
        if span is not None:
            span.finish()


class OpenTracingMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        self._tracer = DjangoTracer(GCPTracer())
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        traced_attributes = []
        self._tracer._apply_tracing(request, view_func, traced_attributes)

    def process_response(self, request, response):
        self._tracer._finish_tracing(request)
        return response
