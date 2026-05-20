import logging
from collections.abc import Iterable

import requests

from exasol.mlflow_plugin.rest_api.data import JsonObject

LOG = logging.getLogger(__name__)
TIMEOUT_IN_SECONDS = 5


class MLflowRestApi:
    def __init__(self, endpoint: str, key: str):
        self.endpoint = endpoint
        self.key = key

    def call(self, params: JsonObject) -> Iterable[JsonObject]:
        page_token = ""  # nosec: B105 - this is not an actual token
        while page_token is not None:
            query = params | {"page_token": page_token}
            raw_respose = requests.post(
                self.endpoint,
                json=query,
                timeout=TIMEOUT_IN_SECONDS,
            )
            resp = raw_respose.json()
            yield from resp.get(self.key, [])
            page_token = resp.get("next_page_token")
            LOG.debug(f"retrieving page {page_token}")
