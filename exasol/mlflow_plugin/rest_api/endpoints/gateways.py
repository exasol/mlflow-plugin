from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.expanding import (
    EXPAND_TAGS,
    Expander,
)

GATEWAY_INPUT_COLUMNS = [
    Column.varchar("provider"),
    Column.varchar("secret_id"),
]

EXPAND_FALLBACK_CONFIG = Expander(
    locator=["fallback_config"],
    output=[
        Column.varchar("fallback_strategy", key="strategy"),
        Column.decimal("fallback_max_attempts", key="max_attempts"),
    ],
)

GATEWAY_ENDPOINTS_LIST = Endpoint(
    var_name="GATEWAY_ENDPOINTS_LIST",
    method="get",
    url_suffix="gateway/endpoints/list",
    output_key="endpoints",
    input_columns=GATEWAY_INPUT_COLUMNS,
    output_columns=[
        Column.varchar("endpoint_id"),
        Column.varchar("name"),
        Column.timestamp("created_at"),
        Column.timestamp("last_updated_at"),
        # Column.varchar("model_mappings"),
        Column.varchar("created_by"),
        Column.varchar("last_updated_by"),
        # Column.varchar("tags"),
        Column.varchar("routing_strategy"),
        # Column.varchar("fallback_config"),
        Column.varchar("experiment_id"),
        Column.boolean("usage_tracking"),

    ],
    expanders=[EXPAND_FALLBACK_CONFIG, EXPAND_TAGS],
    url_prefix="api/3.0/mlflow",
)


GATEWAY_MODEL_DEFINITIONS_LIST = Endpoint(
    var_name="GATEWAY_MODEL_DEFINITIONS_LIST",
    method="get",
    url_suffix="gateway/model-definitions/list",
    output_key="model_definitions",
    input_columns=GATEWAY_INPUT_COLUMNS,
    output_columns=[
        Column.varchar("model_definition_id"),
        Column.varchar("name"),
        Column.varchar("secret_id"),
        Column.varchar("secret_name"),
        Column.varchar("provider"),
        Column.varchar("model_name"),
        Column.timestamp("created_at"),
        Column.timestamp("last_updated_at"),
        Column.varchar("created_by"),
        Column.varchar("last_updated_by"),
    ],
    expanders=[EXPAND_FALLBACK_CONFIG, EXPAND_TAGS],
    url_prefix="api/3.0/mlflow",
)
