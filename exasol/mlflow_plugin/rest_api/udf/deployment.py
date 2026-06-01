import re
from inspect import cleandoc

from pyexasol import (
    ExaConnection,
    ExaStatement,
)

from exasol.mlflow_plugin.rest_api.experiments import ExperimentsSearch
from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import Column

CAMEL_TO_SNAKE_CASE = re.compile(r"(?<!^)(?=[A-Z])")


class Deployable:
    """
    Represents a UDF implementing a call to the MLflow REST API.
    """

    def __init__(
        self,
        language_alias: str,
        db_schema: str,
        api_cls: type[ExperimentsSearch],
        udf_name: str = "",
    ):
        self.language_alias = language_alias
        self.db_schema = db_schema
        self.api_cls = api_cls
        self.udf_name = (
            udf_name or CAMEL_TO_SNAKE_CASE.sub("_", api_cls.__name__).upper()
        )

    @property
    def quoted_name(self) -> str:
        return f'"{self.db_schema}"."{self.udf_name}"'

    @property
    def sql(self) -> str:
        def expander_columns() -> list[Column]:
            return [c for e in self.api_cls.EXPANDERS for c in e.output]

        def sql(columns: list[Column]) -> str:
            return ",\n  ".join(c.sql for c in columns)

        def api_params(columns: list[Column]) -> str:
            return "\n        ".join(f'"{c.name}": ctx.{c.sql_name},' for c in columns)

        input_columns = self.api_cls.INPUT_COLUMNS
        output_columns = self.api_cls.OUTPUT_COLUMNS + expander_columns()
        return cleandoc("""
            --/
            CREATE OR REPLACE {language_alias} SCALAR SCRIPT {udf_name} (
              "connection_name" VARCHAR(2000000),
              {input_columns}
            ) EMITS (
              {output_columns}
            ) AS
            from exasol.mlflow_plugin import rest_api

            body = rest_api.udf.Body(exa, api_cls=rest_api.{class_name})

            def run(ctx):
                body.run(ctx)
            /
            """).format(
            language_alias=self.language_alias,
            udf_name=self.quoted_name,
            class_name=self.api_cls.__name__,
            input_columns=sql(input_columns),
            output_columns=sql(output_columns),
            api_params=api_params(input_columns),
        )

    def deploy(self, pyexasol_connection: ExaConnection) -> ExaStatement:
        return pyexasol_connection.execute(self.sql)


def deploy_all(
    language_alias: str,
    db_schema: str,
    pyexasol_connection: ExaConnection,
) -> None:
    ENDPOINTS = [
        rest_api.ExperimentsSearch,
    ]
    for cls in ENDPOINTS:
        udf = Deployable(language_alias, db_schema, cls)
        udf.deploy(pyexasol_connection)
