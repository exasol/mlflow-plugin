from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    RequestHandler,
    PushdownError,
)


def table_description(endpoint: rest_api.Endpoint) -> JsonObject:
    columns = [c.json for c in endpoint.total_output_columns]
    return {
        "type": "table",
        "name": endpoint.var_name,
        "adapterNotes": "(n/a)",
        "columns": columns,
    }


TABLES = [table_description(e) for e in rest_api.ALL_ENDPOINTS]
SCHEMA_METADATA = {"schemaMetadata": {"tables": TABLES}}


class RestApiRequestHandler(RequestHandler):
    def __init__(self, properties: AdapterProperties):
        super().__init__(properties)

    def _copy(self, request: JsonObject, *keys):
        return {key: req[key] for key in keys if key in request}

    def create(self, request: JsonObject, properties: PropertiesDict) -> JsonObject:
        return self._copy("type") | SCHEMA_METADATA

    def set_properties(
        self, request: JsonObject, properties: PropertiesDict
    ) -> JsonObject:
        return self._copy("type") | SCHEMA_METADATA

    def refresh(self, request: JsonObject) -> JsonObject:
        return self._copy("type", "requestedTables")

    def drop(self, request: JsonObject) -> JsonObject:
        return self._copy("type")

    def get_capabilities(self, request: JsonObject) -> JsonObject:
        return self._copy(request) | {"capabilities": []}

    def pushdown(self, request: JsonObject) -> JsonObject:
        details = req["pushdownRequest"]
        if (pushdown_type := details.get("type")) != "select":
            raise PushdownError(f"Unsupported type {repr(pushdown_type)}")
        if select_list := details.get("selectList"):
            raise PushdownError(f"Unsupported selectList {select_list}")
        return copy("type") | {"sql": "SELECT 1 FROM DUAL"}
