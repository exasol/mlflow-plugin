import re
from inspect import cleandoc
from typing import Type

from pyexasol import (
    ExaConnection,
    ExaStatement,
)

from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin import rest_api

CAMEL_CASE_TO_SNAKE_CASE =  re.compile(r'(?<!^)(?=[A-Z])')


class Deployer:
    def __init__(
        self,
        language_alias: str,
        schema: str,
    ):
        self.language_alias = language_alias
        self.schema = schema

    def render(self, api_cls: Type, name: str = "") -> str:
        def sql(columns: list[Column]) -> str:
            return ",\n  ".join(c.sql for c in columns)

        def api_params(columns: list[Column]) -> str:
            return "\n        ".join(f'"{c.name}": ctx.{c.sql_name},' for c in columns)

        cls_name = api_cls.__name__
        name = name or CAMEL_CASE_TO_SNAKE_CASE.sub('_', cls_name).upper()
        input_columns = api_cls.INPUT_COLUMNS
        output_columns = api_cls.OUTPUT_COLUMNS
        output_columns += [c for e in api_cls.EXPANDERS for c in e.output_columns]
        return cleandoc("""
            --/
            CREATE OR REPLACE {language_alias} SCALAR SCRIPT "{schema}"."{udf_name}" (
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
                schema=self.schema,
                udf_name=name,
                class_name=cls_name,
                input_columns=sql(input_columns),
                output_columns=sql(output_columns),
                api_params=api_params(input_columns),
            )

    def deploy(
        self,
        pyexasol_connection: ExaConnection,
        api_cls: Type,
        name: str = "",
    ) -> ExaStatement:
        sql = self.render(api_cls, name)
        return pyexasol_connection.execute(sql)

    def deploy_all(self, pyexasol_connection: ExaConnection) -> None:
        ENDPOINTS = [
            rest_api.ExperimentsSearch,
        ]
        for cls in ENDPOINTS:
            self.deploy(pyexasol_connection, cls)
