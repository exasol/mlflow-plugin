from collections.abc import Iterable
from typing import Any

from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.processing import PostProcessor
from exasol.mlflow_plugin.rest_api.rest_api import MLflowRestApi


class DataStream:
    """
    Combines basic information like base URI and authentication
    credentials together with endpoint-specific information like method and
    URL suffix and enables retrieving a data stream from the endpoint.
    """

    def __init__(
        self,
        base_uri: str,
        auth: tuple[str, str] | None,
        endpoint: Endpoint,
    ):
        self._api = MLflowRestApi(
            endpoint.method,
            f"{base_uri}/{endpoint.url}",
            key=endpoint.output_key,
            auth=auth,
        )
        self._processor = PostProcessor(
            columns=endpoint.output_columns, expanders=endpoint.expanders
        )

    def retrieve(self, params: JsonObject) -> Iterable[list[Any]]:
        data = self._api.call(params)
        return self._processor.process(data)
