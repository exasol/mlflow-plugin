from collections.abc import Iterable
from typing import Any

from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.processing import PostProcessor
from exasol.mlflow_plugin.rest_api.rest_api import MLflowRestApi


class ApiAdapter:
    def __init__(
        self,
        base_uri: str,
        auth: tuple[str, str] | None,
        endpoint: Endpoint,
    ):
        self._api = MLflowRestApi(
            f"{base_uri}/{endpoint.url_suffix}",
            key=endpoint.output_key,
            auth=auth,
        )
        self._processor = PostProcessor(
            columns=endpoint.output_columns, expanders=endpoint.expanders
        )

    def call(self, params: JsonObject) -> Iterable[list[Any]]:
        data = self._api.call(params)
        return self._processor.process(data)
