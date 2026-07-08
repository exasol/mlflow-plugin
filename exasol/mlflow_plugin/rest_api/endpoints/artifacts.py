from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint

ARTIFACTS_LIST = Endpoint(
    var_name="ARTIFACTS_LIST",
    method="get",
    url_suffix="artifacts",
    output_key="files",
    input_columns=[
        Column.varchar("path"),
    ],
    output_columns=[
        Column.varchar("path"),
        Column.boolean("is_dir"),
        Column.decimal("file_size"),
    ],
    url_prefix="api/2.0/mlflow-artifacts",
)
