from dataclasses import dataclass

from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint


class UdfParameterException(Exception):
    """UDF input parameters don't match the endpoint's input parameters"""


@dataclass
class ExaMetaColumn:
    name: str
    sql_type: str


@dataclass
class ExaMeta:
    input_columns: list[ExaMetaColumn]
    output_columns: list[ExaMetaColumn]


# The number of input columns declared for the UDF deviates from the MLflow
# REST API endpoint.
#
# * UDF: 2 columns "abc" VARCHAR(20),
# * Endpoint: 2 columns "abc" VARCHAR(20),

# UDF parameter "c" doesn't match the MLflow REST API endpoint parameters.
#
# * UDF: 2 columns "abc" VARCHAR(20),
# * Endpoint: 2 columns "abc" VARCHAR(20),


def verify_columns(
    direction: str, actual: list[ExaMetaColumn], expected: list[Column]
) -> None:
    if len(actual) != len(expected):
        raise UdfParameterException(
            f"UDF is declared with {len(actual)} relevant {direction} columns"
            f" while the endpoint expects {len(expected)} {direction} columns."
        )
    for i, c in enumerate(actual):
        act = f'"{c.name}" {c.sql_type.split()[0]}'
        exp = expected[i].sql
        if act != exp:
            raise UdfParameterException(
                f"UDF {direction} parameter {act}"
                f" doesn't match endpoint declaration {exp}."
            )


def verify_udf_parameters(exa_meta: ExaMeta, endpoint: Endpoint) -> None:
    relevant = [c for c in exa_meta.input_columns if c.name != "connection_name"]
    if len(relevant) != len(exa_meta.input_columns) - 1:
        raise UdfParameterException(
            'UDF does not declare input column "connection_name".'
        )
    verify_columns("input", relevant, endpoint.input_columns)
    verify_columns("output", exa_meta.output_columns, endpoint.total_output_columns)
