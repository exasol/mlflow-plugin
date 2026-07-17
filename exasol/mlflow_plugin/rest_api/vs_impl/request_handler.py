from collections.abc import Iterator

import exasol.mlflow_plugin.virtual_schema as vs
from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.exa_meta import ExaMeta
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PropertiesDict,
    Property,
    PropertyValidator,
    PushdownError,
    dget,
)


def find_endpoint(table_name: str) -> rest_api.Endpoint:
    for e in rest_api.ALL_ENDPOINTS:
        if e.virtual_schema_table == table_name:
            return e
    raise PushdownError(f'Unknown table "{table_name}". Couldn\'t find any endpoint.')


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


def udf_call(schema: str, endpoint: rest_api.Endpoint, properties: PropertiesDict):
    def parameters() -> Iterator[str]:
        connection_name = properties.get("CONNECTION_NAME") or "MLFLOW"
        max_results = properties.get("MAX_RESULTS") or "NULL"
        yield f"'{connection_name}'"
        for col in endpoint.input_columns:
            yield max_results if col.name == "max_results" else "NULL"

    comma_sep = ", ".join(parameters())
    # VS API does not support prepared statements
    return f'SELECT "{schema}"."{endpoint.var_name}"({comma_sep})'  # nosec: B608


PROPERTIES = [
    Property("CONNECTION_NAME", str, mandatory=True),
    Property("MAX_RESULTS", int),
]


class RequestHandler(vs.RequestHandler):
    def __init__(self, exa_meta: ExaMeta):
        """
        Parameter exa_meta contains metatada about the UDF / Virtual
        Schema, including the script_schema.

        See
        https://docs.exasol.com/db/latest/database_concepts/udf_scripts/python3.htm#Metadata
        """
        super().__init__()
        self.properties = PropertyValidator(PROPERTIES)
        self.udf_schema = exa_meta.script_schema

    def _property_values(self, request: JsonObject) -> PropertiesDict:
        return dget(request, "schemaMetadataInfo", "properties", default={})

    def _copy(self, request: JsonObject, *keys):
        return {key: request[key] for key in keys if key in request}

    def create(self, request: JsonObject) -> JsonObject:
        self.properties.validate(self._property_values(request), check_mandatory=True)
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
        table = from_clause.get("name")
        endpoint = find_endpoint(table)
        sql = udf_call(self.udf_schema, endpoint, self._property_values(request))
        return self._copy(request, "type") | {"sql": sql}
