from dataclasses import dataclass
from typing import Any

import pyexasol

from exasol.mlflow_plugin.virtual_schema.deployment import Adapter


@dataclass
class VirtualSchema:
    name: str
    adapter: Adapter
    properties: dict[str, Any] | None = None

    def drop(self, con: pyexasol.ExaConnection) -> pyexasol.ExaStatement:
        return con.execute(f'DROP VIRTUAL SCHEMA IF EXISTS "{self.name}" CASCADE')

    def _with_properties(self) -> str:
        if not self.properties:
            return ""
        return " WITH" + "".join(
            f"\n    {k} = '{v}'" for k, v in self.properties.items()
        )

    def create(
        self, con: pyexasol.ExaConnection, replace: bool = False
    ) -> pyexasol.ExaStatement:
        self.adapter.create(con)
        if replace:
            self.drop(con)
        return con.execute(
            f'CREATE VIRTUAL SCHEMA "{self.name}"'
            f" USING {self.adapter.quoted}{self._with_properties()}"
        )
