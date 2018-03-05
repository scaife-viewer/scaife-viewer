import base64
import json
import os

from google.cloud.trace.client import Client
from google.oauth2 import service_account
from opencensus.trace.exporters.stackdriver_exporter import \
    StackdriverExporter as BaseStackdriverExporter


def get_client(**kwargs):
    encoded_key = os.environ.get("GCP_TRACING_SERVICE_ACCOUNT")
    if not encoded_key:
        raise RuntimeError("missing GCP_TRACING_SERVICE_ACCOUNT")
    service_account_key = json.loads(base64.b64decode(encoded_key))
    project_id = service_account_key["project_id"]
    credentials = service_account.Credentials.from_service_account_info(service_account_key)
    scoped_credentials = credentials.with_scopes([
        "https://www.googleapis.com/auth/trace.append",
    ])
    return Client(project=project_id, credentials=scoped_credentials, **kwargs)


class StackdriverExporter(BaseStackdriverExporter):

    def __init__(self, *args, **kwargs):
        super().__init__(get_client(), *args, **kwargs)
