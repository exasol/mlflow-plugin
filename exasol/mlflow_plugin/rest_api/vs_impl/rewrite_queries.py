from collections.abc import Iterator

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PropertiesDict,
    QueryRewriter,
)
from exasol.mlflow_plugin.virtual_schema.dict_utils import dget


def from_clause(request: JsonObject) -> JsonObject:
    return dget(request, "pushdownRequest", "from", default={})


def input_parameters(
    endpoint: rest_api.Endpoint,
    properties: PropertiesDict,
    values: PropertiesDict,
) -> Iterator[str]:
    """
    Args:

        endpoint: The endpoint to return the input parameter values for.

        properties: The properties of the Virtual Schema to read the
            connection name and default parameters values from.

        values: additional values for specific parameters
    """

    connection_name = properties.get("CONNECTION_NAME") or "MLFLOW"
    _values = {
        "max_results": properties.get("MAX_RESULTS") or "NULL",
    } | values
    yield f"'{connection_name}'"
    for col in endpoint.input_columns:
        yield _values.get(col.name) or "NULL"


class TableRewriter(QueryRewriter):
    """
    Rewriter for simple tables, e.g. EXPERIMENTS
    """

    def __init__(self, endpoint: rest_api.Endpoint, table_name: str):
        self.endpoint = endpoint
        self.table_name = table_name

    def can_handle(self, request: JsonObject) -> bool:
        fc = from_clause(request)
        return (fc.get("type"), fc.get("name")) == ("table", self.table_name)

    def rewrite(
        self,
        request: JsonObject,
        properties: PropertiesDict,
        udf_schema: str,
    ) -> str:
        params = input_parameters(self.endpoint, properties, {})
        # VS API does not support prepared statements
        sql = 'SELECT "{udf_schema}"."{udf_name}"({params})'  # nosec: B608
        return sql.format(
            udf_schema=udf_schema,
            udf_name=self.endpoint.var_name,
            params=", ".join(params),
        )
