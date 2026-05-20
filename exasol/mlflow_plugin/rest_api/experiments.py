from typing import (
    Any,
    Iterable,
)

from exasol.mlflow_plugin.rest_api import (
    processing,
    rest_api,
)
from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


class ExperimentsSearch:
    """
    base_uri: e.g. "http://localhost:5000/api/2.0/mlflow/"
    """

    def __init__(self, base_uri: str):
        self._api = rest_api.MLflowRestApi(
            f"{base_uri}/experiments/search",
            key="experiments",
        )
        self._processor = processing.PostProcessor(
            has_tags=True,
            columns=[
                Column("experiment_id", 2, header="ID"),
                Column("name", 15, align="right"),
                Column("artifact_location", 10, align="right"),
                Column("lifecycle_stage", 6),
                Column.timestamp("last_update_time", header="Updated"),
                Column.timestamp("creation_time", header="Created"),
            ],
        )

    def call(
        self,
        filter: str | None = None,
        view_type: str | None = None,
        max_results: int | None = None,
        order_by: list[str] | None = None,
    ) -> Iterable[Any]:
        params = {
            "filter": filter,
            "view_type": view_type,
            "max_results": max_results,
            "order_by": order_by,
        }
        data = self._api.call(params)
        return self._processor.process(data)

    def _call(self, params: JsonObject) -> Iterable[Any]:
        params = {"max_results": 10} | params
        data = self._api.call(params)
        return self._processor.process(data)
