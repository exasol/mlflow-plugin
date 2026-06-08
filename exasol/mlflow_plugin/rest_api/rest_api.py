from __future__ import annotations

import logging
from collections.abc import Iterable

import requests

from exasol.mlflow_plugin.rest_api.data import JsonObject

LOG = logging.getLogger(__name__)
TIMEOUT_IN_SECONDS = 5


class RestApiError(Exception):
    """A call to MLflow REST API returned a status_code other than 200"""

    def __init__(
        self,
        method: str,
        endpoint: str,
        query: JsonObject,
        response: requests.Response,
    ):
        super().__init__(
            f"{method.upper()} request to endpoint {endpoint}"
            f" with query {query} returned"
            f" status code {response.status_code}: {response.reason}."
        )


class MLflowRestApi:
    def __init__(
        self,
        method: str,
        endpoint: str,
        key: str,
        auth: tuple[str, str] | None,
    ):
        self.method = method
        self.endpoint = endpoint
        self.key = key
        self.auth = auth

    def call(self, params: JsonObject) -> Iterable[JsonObject]:
        query: JsonObject = {"max_results": 1000}
        query |= {k: v for k, v in params.items() if v is not None}
        page_token = ""  # nosec: B105 - this is not an actual token
        while page_token is not None:
            query = query | {"page_token": page_token}
            raw_response = requests.request(
                self.method,
                self.endpoint,
                json=query,
                timeout=TIMEOUT_IN_SECONDS,
                auth=self.auth,
            )
            if raw_response.status_code != 200:
                raise RestApiError(self.method, self.endpoint, query, raw_response)
            resp = raw_response.json()
            content = resp.get(self.key, []) if self.key else resp
            yield from [content] if isinstance(content, dict) else content
            page_token = resp.get("next_page_token")
            LOG.debug("retrieving page %s", page_token)
