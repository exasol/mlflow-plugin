from typing import Protocol

from exasol.mlflow_plugin.virtual_schema.types import (
    JsonObject,
    PropertiesDict,
)


class QueryRewriter(Protocol):
    def can_handle(self, request: JsonObject) -> bool:
        """
        Whether the current QueryRewriter can handle the specified request
        to the Virtual Schema API.
        """

    def rewrite(
        self,
        request: JsonObject,
        properties: PropertiesDict,
        udf_schema: str,
    ) -> str:
        """
        Rewrite specified request to the Virtual Schema API and return the
        resulting SQL statement.
        """
