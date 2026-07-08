import re
from dataclasses import (
    dataclass,
    field,
)

from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.expanding import Expander

VIRTUAL_SCHEMA_TABLE_PATTERN = re.compile(r"(_LIST|_SEARCH|S_GET|_GET)$")


@dataclass
class Endpoint:
    var_name: str
    method: str
    url_suffix: str
    output_key: str
    input_columns: list[Column]
    output_columns: list[Column]
    expanders: list[Expander] = field(default_factory=list)
    url_prefix: str = "api/2.0/mlflow"

    @property
    def virtual_schema_table(self) -> str:
        return VIRTUAL_SCHEMA_TABLE_PATTERN.sub("", self.var_name)

    @property
    def url(self) -> str:
        return f"{self.url_prefix}/{self.url_suffix}"

    @property
    def expander_columns(self) -> list[Column]:
        return [c for e in self.expanders for c in e.output]

    @property
    def total_output_columns(self) -> list[Column]:
        return self.output_columns + self.expander_columns
