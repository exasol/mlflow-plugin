from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.endpoints.input_columns import SEARCH_COLUMNS
from exasol.mlflow_plugin.rest_api.expanding import EXPAND_TAGS

MODEL_VERSION_COLUMNS = [
    Column.varchar("name"),
    Column.varchar("version"),
    Column.timestamp("creation_timestamp", sql_name="created"),
    Column.timestamp("last_updated_timestamp", sql_name="updated"),
    Column.varchar("user_id"),
    Column.varchar("current_stage"),
    Column.varchar("description"),
    Column.varchar("source"),
    Column.varchar("run_id"),
    Column.varchar("status"),
    Column.varchar("status_message"),
    Column.varchar("run_link"),
    Column.varchar("aliases"),
    Column.varchar("model_id"),
]

MODEL_VERSION_INPUT_COLUMNS = [
    Column.varchar("name", comment="mandatory"),
    Column.varchar("version", comment="mandatory"),
]

MODEL_VERSIONS_GET = Endpoint(
    var_name="MODEL_VERSIONS_GET",
    method="get",
    url_suffix="model-versions/get",
    output_key="model_version",
    input_columns=MODEL_VERSION_INPUT_COLUMNS,
    output_columns=MODEL_VERSION_COLUMNS,
    expanders=[EXPAND_TAGS],
)

MODEL_VERSIONS_GET_DOWNLOAD_URI = Endpoint(
    var_name="MODEL_VERSIONS_GET_DOWNLOAD_URI",
    method="get",
    url_suffix="model-versions/get-download-uri",
    output_key="",
    input_columns=MODEL_VERSION_INPUT_COLUMNS,
    output_columns=[Column.varchar("artifact_uri")],
    expanders=[],
)

MODEL_VERSIONS_SEARCH = Endpoint(
    var_name="MODEL_VERSIONS_SEARCH",
    method="get",
    url_suffix="model-versions/search",
    output_key="model_versions",
    input_columns=SEARCH_COLUMNS,
    output_columns=MODEL_VERSION_COLUMNS,
    expanders=[EXPAND_TAGS],
)

REGISTERED_MODELS_GET_LATEST_VERSIONS = Endpoint(
    var_name="REGISTERED_MODELS_GET_LATEST_VERSIONS",
    method="post",
    url_suffix="registered-models/get-latest-versions",
    output_key="model_versions",
    input_columns=[
        Column.varchar("name", comment="mandatory"),
        Column.varchar("stages", comma_sep=True),
    ],
    output_columns=MODEL_VERSION_COLUMNS,
    expanders=[EXPAND_TAGS],
)
