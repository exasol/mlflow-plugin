from inspect import cleandoc

from exasol.mlflow_plugin.rest_api.data import Column


def render(
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
        language_alias=language_alias,
        schema=schema,
        udf_name=name,
        class_name=class_name,
        input_columns=sql(input_columns),
        output_columns=sql(output_columns),
        api_params=api_params(input_columns),
    )


# UDFS = [
#     (ExperimentsSearch, "EXPERIMENTS_SEARCH", "experiments_search_udf.sql"),
# ]
#
# def render_all(language_alias: str, schema: str):
#     for cls, udf_name in UDFS:
#         output_columns = cls.OUTPUT_COLUMNS
#         output_columns += [c for e in cls.EXPANDERS for c in e.output_columns]
#         render(
#             language_alias=language_alias,
#             schema=schema,
#             name=udf_name,
#             class_name=cls.__name__,
#             input_columns=cls.INPUT_COLUMNS,
#             output_columns=output_columns,
#         )
