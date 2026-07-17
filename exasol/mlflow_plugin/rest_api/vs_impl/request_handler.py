from test.integration.virtual_schema.resources.adapter_impl import dget

import exasol.mlflow_plugin.virtual_schema as vs
from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.exa_meta import ExaMeta
from exasol.mlflow_plugin.virtual_schema import (
    AdapterProperties,
    JsonObject,
    PushdownError,
)


def tables() -> list[JsonObject]:
    def table_description(endpoint: rest_api.Endpoint) -> JsonObject:
        columns = [c.json for c in endpoint.total_output_columns]
        return {
            "type": "table",
            "name": endpoint.virtual_schema_table,
            "columns": columns,
        }

    return [
        table_description(e) for e in rest_api.ALL_ENDPOINTS if e.virtual_schema_table
    ]


def udf_call(schema: str, connection_name: str, table: str):
    endpoint = next(
        e for e in rest_api.ALL_ENDPOINTS if e.virtual_schema_table == table
    )
    f"SELECT * from {endpoint.var_name}"
    args = [f"'{connection_name}'"] + ["NULL" for _ in endpoint.input_columns]
    comma_sep = ", ".join(args)
    # VS API does not support prepared statements
    return f'SELECT "{schema}"."{endpoint.var_name}"({comma_sep})'  # nosec: B608



class RequestHandler(vs.RequestHandler):
    def __init__(self, exa_meta: ExaMeta):
        """
        Args:

            udf_schema: Name of the database schema containing the UDFs for
                accessing the MLflow REST API
        """

        super().__init__()
        self.properties = AdapterProperties(["CONNECTION_NAME", "MAX_RESULTS"])
        self.udf_schema = exa_meta.script_schema

    def _property_values(self, request: JsonObject) -> JsonObject:
        return dget(request, "schemaMetadataInfo", "properties", default={})

    def _copy(self, request: JsonObject, *keys):
        return {key: request[key] for key in keys if key in request}

    def create(self, request: JsonObject) -> JsonObject:
        self.properties.validate(self._property_values(request))
        metadata = {"schemaMetadata": {"tables": tables()}}
        return self._copy(request, "type") | metadata

    def set_properties(self, request: JsonObject) -> JsonObject:
        values = dget(request, "properties", default={})
        self.properties.validate(values)
        return self._copy(request, "type")

    def refresh(self, request: JsonObject) -> JsonObject:
        return self._copy(request, "type")

    def drop(self, request: JsonObject) -> JsonObject:
        return self._copy(request, "type")

    def get_capabilities(self, request: JsonObject) -> JsonObject:
        return self._copy(request, "type") | {"capabilities": []}

    def pushdown(self, request: JsonObject) -> JsonObject:
        details = request["pushdownRequest"]
        if (pushdown_type := details.get("type")) != "select":
            raise PushdownError(f"Unsupported pushdown type {repr(pushdown_type)}")
        if select_list := details.get("selectList"):
            raise PushdownError(f"Unsupported selectList {select_list}")
        from_clause = details.get("from", {})
        if (from_type := from_clause.get("type")) != "table":
            raise PushdownError(f"Unsupported FROM type {from_type}")
        connection_name = self._property_values(request).get("CONNECTION_NAME", "")
        table = from_clause.get("name")
        sql = udf_call(self.udf_schema, connection_name, table)
        return self._copy(request, "type") | {"sql": sql}
