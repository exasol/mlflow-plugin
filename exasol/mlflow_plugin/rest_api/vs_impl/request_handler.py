import exasol.mlflow_plugin.virtual_schema as vs
from exasol.mlflow_plugin import rest_api
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


class RequestHandler(vs.RequestHandler):
    def __init__(self, properties: AdapterProperties):
        super().__init__(properties)

    def _copy(self, request: JsonObject, *keys):
        return {key: request[key] for key in keys if key in request}

    def create(self, request: JsonObject) -> JsonObject:
        metadata = {"schemaMetadata": {"tables": tables()}}
        return self._copy(request, "type") | metadata

    def set_properties(self, request: JsonObject) -> JsonObject:
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
            raise PushdownError(f"Unsupported type {repr(pushdown_type)}")
        if select_list := details.get("selectList"):
            raise PushdownError(f"Unsupported selectList {select_list}")
        return self._copy(request, "type") | {"sql": "SELECT 1 FROM DUAL"}
