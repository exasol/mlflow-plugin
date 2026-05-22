import logging
from collections.abc import Iterable

import requests

from exasol.mlflow_plugin.rest_api.data import JsonObject

LOG = logging.getLogger(__name__)
TIMEOUT_IN_SECONDS = 5


class MLflowRestApi:
    def __init__(self, endpoint: str, key: str, auth: tuple[str, str] | None = None):
        self.endpoint = endpoint
        self.key = key
        self.auth = auth or ("", "")

    def call(self, params: JsonObject) -> Iterable[JsonObject]:
        query: JsonObject = {"max_results": 1000}
        query |= {k: v for k, v in params.items() if v is not None}
        page_token = ""  # nosec: B105 - this is not an actual token
        while page_token is not None:
            query = query | {"page_token": page_token}
            raw_respose = requests.post(
                self.endpoint,
                json=query,
                timeout=TIMEOUT_IN_SECONDS,
                auth=self.auth,
            )
            resp = raw_respose.json()
            yield from resp.get(self.key, [])
            page_token = resp.get("next_page_token")
            LOG.debug("retrieving page %s", page_token)
