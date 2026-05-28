from abc import abstractmethod
from typing import (
    Iterable,
    TypeVar,
)

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


def _nested(element: JsonObject, locator: list[str]) -> list[JsonObject]:
    """
    Use the keys in arg ``locator`` to navigate into the specified
    JsonObject and retrieve the nested value. Return the provided defult value
    if any of the keys is not contained in the JsonObject.
    """

    current = element
    for key in locator:
        if key not in current:
            return [{}]
        current = current[key]  # type: ignore
    return current if isinstance(current, list) else [current]


class Expander:
    """
    Expands a stream of input elements by adding entries to each element
    or by emitting additional elements.
    """

    def __init__(self, locator: list[str], output: list[Column]):
        self.locator = locator
        self.output = output
        self._default = {o.name: None for o in self.output}

    def flatten_element(self, values: JsonObject) -> JsonObject:
        if not values:
            return self._default
        return {o.name: values[o.key] for o in self.output}

    def expand(self, data: Iterable[JsonObject]) -> Iterable[JsonObject]:
        return (
            d | self.flatten_element(element)
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
