from collections.abc import Iterable
from typing import (
    Any,
)

from exasol.mlflow_plugin.rest_api import (
    expanding,
    processing,
    rest_api,
)
from exasol.mlflow_plugin.rest_api.data import (
    Column,
)


class ExperimentsSearch:
    INPUT_COLUMNS = [
        Column.varchar("filter"),
        Column.varchar("view_type"),
        Column.varchar("order_by", comma_sep=True),
        Column.decimal("max_results"),
    ]
    OUTPUT_COLUMNS = [
        Column.varchar("experiment_id"),
        Column.varchar("name"),
        Column.varchar("artifact_location"),
        Column.varchar("lifecycle_stage"),
        Column.timestamp("last_update_time", sql_name="updated"),
        Column.timestamp("creation_time", sql_name="created"),
    ]
    EXPANDERS = [expanding.EXPAND_TAGS]

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
    def param_names(cls) -> list[str]:
        return [c.name for c in cls.INPUT_COLUMNS]

    def params(self, *values: Any) -> dict[str, Any]:
        def convert(column: Column, v: Any) -> Any:
            return v.split(",") if column.comma_sep else v

        return {
            c.name: convert(c, v)
            for c, v in zip(self.INPUT_COLUMNS, values)
            if v is not None
        }

    def call(
        self,
        filter: str | None = None,
        view_type: str | None = None,
        order_by: str | None = None,
        max_results: int | None = None,
    ) -> Iterable[Any]:
        params = self.params(filter, view_type, order_by, max_results)
        data = self._api.call(params)
        return self._processor.process(data)
