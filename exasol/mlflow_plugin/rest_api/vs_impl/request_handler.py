import exasol.mlflow_plugin.virtual_schema as vs
from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.exa_meta import ExaMeta
from exasol.mlflow_plugin.rest_api.vs_impl.rewrite_queries import (
    QueryRewriter,
    TableRewriter,
    TableRewriterWithSubQuery,
    from_clause,
)
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PropertiesDict,
    Property,
    PropertyValidator,
    PushdownError,
    dget,
)

VALIDATOR = PropertyValidator(
    [
        Property("CONNECTION_NAME", str, mandatory=True),
        Property("MAX_RESULTS", int),
    ]
)

REWRITERS: list[QueryRewriter] = [
    TableRewriter(rest_api.ARTIFACTS_LIST, "ARTIFACTS"),
    TableRewriter(rest_api.EXPERIMENTS_SEARCH, "EXPERIMENTS"),
    TableRewriter(rest_api.GATEWAY_ENDPOINTS_LIST, "GATEWAY_ENDPOINTS"),
    TableRewriter(
        rest_api.GATEWAY_MODEL_DEFINITIONS_LIST,
        "GATEWAY_MODEL_DEFINITIONS",
    ),
    TableRewriter(rest_api.MODEL_VERSIONS_SEARCH, "MODEL_VERSIONS"),
    TableRewriter(rest_api.REGISTERED_MODELS_SEARCH, "REGISTERED_MODELS"),
    TableRewriterWithSubQuery(
        rest_api.REGISTERED_MODELS_GET_LATEST_VERSIONS,
        "REGISTERED_MODELS_LATEST_VERSIONS",
        input_params={"name": 'AUX."name"'},
        aux_endpoint=rest_api.REGISTERED_MODELS_SEARCH,
    ),
    TableRewriterWithSubQuery(
        rest_api.RUNS_SEARCH,
        "RUNS",
        input_params={"experiment_ids": 'AUX."experiment_id"'},
        aux_endpoint=rest_api.EXPERIMENTS_SEARCH,
    ),
]


class RequestHandler(vs.RequestHandler):
    def __init__(
        self,
        exa_meta: ExaMeta,
        properties: PropertyValidator = VALIDATOR,
        rewriters: list[QueryRewriter] | None = None,
    ):
        """
        Parameter exa_meta contains metatada about the UDF / Virtual
        Schema, including the script_schema.

        See
        https://docs.exasol.com/db/latest/database_concepts/udf_scripts/python3.htm#Metadata
        """
        super().__init__()
        self.udf_schema = exa_meta.script_schema
        self.properties = properties
        self.rewriters = rewriters or REWRITERS

    def _property_values(self, request: JsonObject) -> PropertiesDict:
        return dget(request, "schemaMetadataInfo", "properties", default={})

    def _copy(self, request: JsonObject, *keys):
        return {key: request[key] for key in keys if key in request}

    @property
    def _tables(self) -> list[JsonObject]:
        def table(rewriter: TableRewriter) -> JsonObject:
            columns = [c.json for c in rewriter.endpoint.total_output_columns]
            return {"type": "table", "name": rewriter.table_name, "columns": columns}

        return [table(w) for w in self.rewriters if isinstance(w, TableRewriter)]

    def create(self, request: JsonObject) -> JsonObject:
        self.properties.validate(self._property_values(request), check_mandatory=True)
        metadata = {"schemaMetadata": {"tables": self._tables}}
        return self._copy(request, "type") | metadata

    def set_properties(self, request: JsonObject) -> JsonObject:
        values = dget(request, "properties", default={})
        merged = self._property_values(request) | values
        self.properties.validate(merged, check_mandatory=True)
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

        for rewriter in self.rewriters:
            if rewriter.can_handle(request):
                properties = self._property_values(request)
                sql = rewriter.rewrite(request, properties, self.udf_schema)
                return self._copy(request, "type") | {"sql": sql}

        raise PushdownError(f"Unsupported Pushdown from clause {from_clause(request)}")
