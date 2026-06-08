from collections.abc import Iterable
from typing import Any

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)
from exasol.mlflow_plugin.rest_api.expanding import Expander


class PostProcessor:
    """
    Process the generic Json response from MLflow REST API and return only
    the values in the order of the columns.

    The keys of the original Json response are ommitted.

    Columns with array values are expanded by repeating the other columns with
    additional columns c_i, representing one element of the original array
    value.
    """

    def __init__(self, columns: list[Column], expanders: list[Expander] | None = None):
        self.expanders = expanders or []
        self.columns = columns + [c for e in self.expanders for c in e.output]

    def process(self, stream: Iterable[JsonObject]) -> Iterable[list[Any]]:
        def col_value(row: JsonObject, column: Column) -> Any:
            value = row.get(column.name)
            return column.process(value)

        def row(row: JsonObject) -> list[Any]:
            return [col_value(row, c) for c in self.columns]

        for expander in self.expanders:
            stream = expander.expand(stream)
        return (row(data) for data in stream)
