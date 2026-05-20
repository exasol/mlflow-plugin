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
        self.columns = columns + [c for e in self.expanders for c in e.columns]

    def process(self, data: Iterable[JsonObject]) -> Iterable[list[Any]]:
        for expander in self.expanders:
            data = expander.expand(data)
        return ([c.process(el.get(c.name)) for c in self.columns] for el in data)
