from collections.abc import Iterable
from inspect import cleandoc
from typing import (
    Any,
)

from exasol.mlflow_plugin.rest_api import (
    processing,
    rest_api,
)
from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)
from exasol.mlflow_plugin.rest_api.expanding import (
    EXPAND_TAGS,
)

from exasol.mlflow_plugin.rest_api.expanding import EXPAND_TAGS


def render_udf(
    language_alias: str,
    schema: str,
    name: str,
    class_name: str,
    input_columns: list[Column],
    output_columns: list[Column],
) -> str:
    def sql(columns: list[Column]) -> str:
        return ",\n  ".join(c.sql for c in columns)

    def api_params(columns: list[Column]) -> str:
        return "\n        ".join(f'"{c.name}": ctx.{c.sql_name},' for c in columns)

    return cleandoc("""
    --/
    CREATE OR REPLACE {language_alias} SCALAR SCRIPT "{schema}"."{udf_name}" (
      {input_columns}
    ) EMITS (
      {output_columns}
    ) AS
    from exasol.mlflow_plugin.rest_api import {class_name}

    def run(ctx):
        # probably depends on a connection object
        endpoint = {class_name}("URI", ("admin", "password1234"))
        params = {{
            {api_params}
        }}
        for row in endpoint.call(**params):
            ctx.emit(*row))
    /
    """).format(
        language_alias=language_alias,
        schema=schema,
        udf_name=name,
        class_name=class_name,
        input_columns=sql(input_columns),
        output_columns=sql(output_columns),
        api_params=api_params(input_columns),
    )


class ExperimentsSearch:
    """
    base_uri: e.g. "http://localhost:5000/api/2.0/mlflow"
    """

    def __init__(self, base_uri: str, auth: tuple[str, str] | None = None):
        self.input_columns = [
            Column("filter", 2000),
            Column("view_type", 2000),
            Column("order_by", 2000),
            Column("max_results", 20, data_type="int"),
        ]
        self._api = rest_api.MLflowRestApi(
            f"{base_uri}/experiments/search",
            key="experiments",
            auth=auth,
        )
        self._processor = processing.PostProcessor(
            columns=[
                Column("experiment_id", 2, sql_name="ID"),
                Column("name", 15),
                Column("artifact_location", 10),
                Column("lifecycle_stage", 6),
                Column.timestamp("last_update_time", sql_name="UPDATED"),
                Column.timestamp("creation_time", sql_name="CREATED"),
            ],
            expanders=[EXPAND_TAGS],
        )

    @property
    def udf(self) -> str:
        return render_udf(
            language_alias="MLFLOW",
            schema="MLFLOW_REST_API",
            name="EXPERIMENTS_SEARCH",
            class_name=type(self).__name__,
            input_columns=self.input_columns,
            output_columns=self._processor.columns,
        )

    def call(
        self,
        filter: str | None = None,
        view_type: str | None = None,
        order_by: list[str] | None = None,
        max_results: int | None = None,
    ) -> Iterable[Any]:
        values = (filter, view_type, order_by, max_results)
        params = dict(zip((p.name for p in self.input_columns), values))
        data = self._api.call(params)
        return self._processor.process(data)
