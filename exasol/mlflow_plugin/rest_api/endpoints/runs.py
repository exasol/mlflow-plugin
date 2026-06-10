from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.expanding import Expander

EXPAND_RUN_INFO = Expander(
    locator=["info"],
    output=[
        Column.varchar("run_id"),
        Column.varchar("run_uuid"),
        Column.varchar("run_name"),
        Column.varchar("experiment_id"),
        Column.varchar("user_id"),
        Column.varchar("status"),
        Column.timestamp("start_time"),
        Column.timestamp("end_time"),
        Column.varchar("artifact_uri"),
        Column.varchar("lifecycle_stage"),
    ],
)


EXPAND_DATA_TAGS = Expander(
    locator=["data", "tags"],
    output=[
        Column.varchar("tag_key", key="key"),
        Column.varchar("tag_value", key="value"),
    ],
)


RUNS_SEARCH = Endpoint(
    var_name="RUNS_SEARCH",
    method="post",
    url_suffix="runs/search",
    output_key="runs",
    input_columns=[
        Column.varchar("experiment_ids", comma_sep=True),
        Column.varchar("filter"),
        Column.varchar("run_view_type"),
        Column.varchar("order_by", comma_sep=True),
        Column.decimal("max_results"),
    ],
    output_columns=[],
    expanders=[EXPAND_RUN_INFO, EXPAND_DATA_TAGS],
)
