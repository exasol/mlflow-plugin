from exasol.mlflow_plugin.rest_api import (
    expanding,
)
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint

EXPERIMENTS_SEARCH = Endpoint(
    var_name="EXPERIMENTS_SEARCH",
    method="post",
    url_suffix="experiments/search",
    output_key="experiments",
    input_columns=[
        Column.varchar("filter"),
        Column.varchar("view_type"),
        Column.varchar("order_by", comma_sep=True),
        Column.decimal("max_results"),
    ],
    output_columns=[
        Column.varchar("experiment_id"),
        Column.varchar("name"),
        Column.varchar("artifact_location"),
        Column.varchar("lifecycle_stage"),
        Column.timestamp("last_update_time", sql_name="updated"),
        Column.timestamp("creation_time", sql_name="created"),
    ],
    expanders=[expanding.EXPAND_TAGS],
)
