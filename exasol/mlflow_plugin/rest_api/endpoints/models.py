from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.endpoints.input_columns import SEARCH_COLUMNS
from exasol.mlflow_plugin.rest_api.expanding import EXPAND_TAGS

REGISTERED_MODEL_COLUMNS = [
    Column.varchar("name"),
    Column.timestamp("creation_timestamp", sql_name="created"),
    Column.timestamp("last_updated_timestamp", sql_name="updated"),
    Column.varchar("user_id"),
    Column.varchar("description"),
    Column.varchar("deployment_job_id"),
    Column.varchar("deployment_job_state"),
]

REGISTERED_MODEL_GET = Endpoint(
    var_name="REGISTERED_MODEL_GET",
    method="get",
    url_suffix="registered-models/get",
    output_key="registered_model",
    input_columns=[
        Column.varchar("name"),
    ],
    output_columns=REGISTERED_MODEL_COLUMNS,
    expanders=[EXPAND_TAGS],
)

REGISTERED_MODELS_SEARCH = Endpoint(
    var_name="REGISTERED_MODELS_SEARCH",
    method="get",
    url_suffix="registered-models/search",
    output_key="registered_models",
    input_columns=SEARCH_COLUMNS,
    output_columns=REGISTERED_MODEL_COLUMNS,
    expanders=[EXPAND_TAGS],
)
