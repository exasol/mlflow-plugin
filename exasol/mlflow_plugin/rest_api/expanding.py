from collections.abc import Iterable

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


class Expander:
    """
    Specifies rules to expand a single source column into multiple output
    columns by iterating the values of an array contained in the source
    column.

    E.g. source column "tags" containing an array of key/value pairs can be
    expanded by repeating the same row of data, each instance with a single
    key/value pair in 2 output columns.
    """

    def __init__(self, source: str, columns: list[Column]):
        self.source = source
        self.columns = columns
        self._default = [{c.key: None for c in self.columns}]

    def expand(self, data: Iterable[JsonObject]) -> Iterable[JsonObject]:
        def additional_columns(values: JsonObject) -> JsonObject:
            return {c.name: values[c.key] for c in self.columns}

        return (
            d | additional_columns(tag)
            for d in data
            for tag in d.get(self.source, self._default)
        )


EXPAND_TAGS = Expander(
    "tags",
    [
        Column("tag_key", 15, key="key"),
        Column("tag_value", 15, key="value"),
    ],
)
