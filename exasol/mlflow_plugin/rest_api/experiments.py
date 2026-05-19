from exasol.mlflow_plugin.rest_api.column import Column
from exasol.mlflow_plugin.rest_api.rest_api import (
    JsonObject,
    MLflowRestApi,
)


class ExperimentsSearch(MLflowRestApi):
    """
    base_uri: e.g. "http://localhost:5000/api/2.0/mlflow/"
    """

    def __init__(self, base_uri: str, params: JsonObject):
        super().__init__(
            f"{base_uri}/experiments/search",
            params={"max_results": 10} | params,
            key="experiments",
            has_tags=True,
            columns=[
                Column("experiment_id", 2, header="ID"),
                Column("name", 15, align="right"),
                Column("artifact_location", 10, align="right"),
                Column("lifecycle_stage", 6),
                Column.timestamp("last_update_time", header="Updated"),
                Column.timestamp("creation_time", header="Created"),
            ],
        )
