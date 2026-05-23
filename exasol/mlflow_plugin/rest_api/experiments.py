from collections.abc import Iterable
from inspect import cleandoc
from typing import (
    Any,
)

from exasol.mlflow_plugin.rest_api import (
    processing,
    rest_api,
)
from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)
from exasol.mlflow_plugin.rest_api.expanding import (
    EXPAND_TAGS,
)

from exasol.mlflow_plugin.rest_api.expanding import EXPAND_TAGS


class ExperimentsSearch:
    INPUT_COLUMNS = [
        Column.varchar("filter"),
        Column.varchar("view_type"),
        Column.varchar("order_by"),
        Column.decimal("max_results"),
    ]
    OUTPUT_COLUMNS = [
        Column.varchar("experiment_id", sql_name="id"),
        Column.varchar("name"),
        Column.varchar("artifact_location"),
        Column.varchar("lifecycle_stage"),
        Column.timestamp("last_update_time", sql_name="updated"),
        Column.timestamp("creation_time", sql_name="created"),
    ]
    EXPANDERS = [EXPAND_TAGS]

    def __init__(self, base_uri: str, auth: tuple[str, str] | None = None):
        """
        base_uri: e.g. "http://localhost:5000/api/2.0/mlflow"
        """
        self._api = rest_api.MLflowRestApi(
            f"{base_uri}/experiments/search",
            key="experiments",
            auth=auth,
        )
        self._processor = processing.PostProcessor(
            columns=self.OUTPUT_COLUMNS, expanders=self.EXPANDERS
        )

    @classmethod
    @property
    def param_names(cls) -> list[str]:
        return [c.name for c in cls.INPUT_COLUMNS]

    def call(
        self,
        filter: str | None = None,
        view_type: str | None = None,
        order_by: str | None = None,
        max_results: int | None = None,
    ) -> Iterable[Any]:
        order_by = order_by.split(",") if order_by else None
        values = (filter, view_type, order_by, max_results)
        params = dict(zip((p.name for p in self.INPUT_COLUMNS), values))
        data = self._api.call(params)
        return self._processor.process(data)
