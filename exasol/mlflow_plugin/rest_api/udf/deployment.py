from inspect import cleandoc

from pyexasol import (
    ExaConnection,
    ExaStatement,
)

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint


class Deployable:
    """
    Represents a UDF implementing a call to the MLflow REST API.
    """

    def __init__(
        self,
        language_alias: str,
        db_schema: str,
        endpoint: Endpoint,
        udf_name: str = "",
    ):
        self.language_alias = language_alias
        self.db_schema = db_schema
        self.endpoint = endpoint
        self.udf_name = udf_name or endpoint.var_name

    @property
    def quoted_name(self) -> str:
        prefix = f'"{self.db_schema}".' if self.db_schema else ""
        return f'{prefix}"{self.udf_name}"'

    @property
    def sql(self) -> str:
        def sql(columns: list[Column]) -> str:
            return ",\n  ".join(c.sql for c in columns)

        input_columns = self.endpoint.input_columns
        output_columns = self.endpoint.total_output_columns
        return cleandoc("""
            --/
            CREATE OR REPLACE {language_alias} SCALAR SCRIPT {udf_name} (
              "connection_name" VARCHAR(2000000),
              {input_columns}
            ) EMITS (
              {output_columns}
            ) AS
            from exasol.mlflow_plugin import rest_api

            udf_call = rest_api.UdfCall(exa, endpoint=rest_api.{endpoint_var})

            def run(ctx):
                udf_call.run(ctx)
            /
            """).format(
            language_alias=self.language_alias,
            udf_name=self.quoted_name,
            input_columns=sql(input_columns),
            output_columns=sql(output_columns),
            endpoint_var=self.endpoint.var_name,
        )

    def deploy(self, pyexasol_connection: ExaConnection) -> ExaStatement:
        return pyexasol_connection.execute(self.sql)


def deploy_all(
    language_alias: str,
    db_schema: str,
    pyexasol_connection: ExaConnection,
) -> None:
    for endpoint in rest_api.ALL_ENDPOINTS:
        udf = Deployable(language_alias, db_schema, endpoint)
        udf.deploy(pyexasol_connection)
