from dataclasses import (
    dataclass,
    field,
)

from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.expanding import Expander


@dataclass
class Endpoint:
    var_name: str
    method: str
    url_suffix: str
    output_key: str
    input_columns: list[Column]
    output_columns: list[Column]
    expanders: list[Expander] = field(default_factory=list)

    @property
    def expander_columns(self) -> list[Column]:
        return [c for e in self.expanders for c in e.output]
