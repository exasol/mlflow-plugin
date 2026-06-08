from collections.abc import Iterable

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


def _nested(element: JsonObject, locator: list[str]) -> list[JsonObject]:
    """
    Retrieve the JsonObject's value at the location specified by the
    sequence of keys in ``locator``.  if any of the keys is not contained in
    the surrounding JsonObject return a list with an empty JsonObject.
    """

    current = element
    for key in locator:
        if key not in current:
            return [{}]
        current = current[key]  # type: ignore
    return current if isinstance(current, list) else [current]


class Expander:
    """
    Expands a stream of input elements by emitting additional elements or
    adding entries to each input element.
    """

    def __init__(self, locator: list[str], output: list[Column]):
        self.locator = locator
        self.output = output
        self._default = {o.name: None for o in self.output}

    def expand(self, data: Iterable[JsonObject]) -> Iterable[JsonObject]:
        def flatten_element(values: JsonObject) -> JsonObject:
            if not values:
                return self._default
            return {o.name: values[o.key] for o in self.output}

        return (
            d | flatten_element(element)
            for d in data
            for element in _nested(d, self.locator)
        )


EXPAND_TAGS = Expander(
    locator=["tags"],
    output=[
        Column.varchar("tag_key", key="key"),
        Column.varchar("tag_value", key="value"),
    ],
)
