from collections.abc import Iterable

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


class Expander:
    """
    Expands the array value for a single input_key into multiple output
    columns.

    E.g. the value for input_key "tags" containing an array of key/value pairs
    can be expanded by repeating the current data row, each instance with a
    single key/value pair in 2 additional output columns.
    """

    def __init__(self, input_key: str, output_columns: list[Column]):
        self.input_key = input_key
        self.output_columns = output_columns
        self._default = [{c.key: None for c in self.output_columns}]

    def expand(self, data: Iterable[JsonObject]) -> Iterable[JsonObject]:
        def flatten_element(values: JsonObject) -> JsonObject:
            return {c.name: values[c.key] for c in self.output_columns}

        return (
            d | flatten_element(element)
            for d in data
            for element in d.get(self.input_key, self._default)
        )


EXPAND_TAGS = Expander(
    "tags",
    [
        Column.varchar("tag_key", key="key"),
        Column.varchar("tag_value", key="value"),
    ],
)
