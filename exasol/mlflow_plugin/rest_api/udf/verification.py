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


def verify_columns(actual: list[ExaMetaColumn], expected: list[Column]) -> None:
    if len(actual) != len(expected):
        raise UdfParameterException(
            f"UDF is declared with {len(actual)} relevant input columns"
            f" while the endpoint expects {len(expected)} input columns."
        )
    for i, c in enumerate(actual):
        act = f'"{c.name}" {c.sql_type.split()[0]}'
        exp = expected[i].sql
        if act != exp:
            raise UdfParameterException(
                f'UDF input parameter {act} doesn\'t match endpoint declaration {exp}.'
            )
    # exa.meta.input_columns[]
    # [Col(name='a', length=200, sql_type='VARCHAR(200) UTF8', type=<class 'str'>, precision=None, scale=None)]


def verify_udf_parameters(exa: ExaMeta, endpoint: Endpoint) -> None:
    relevant = [c for c in exa.input_columns if c.name != "connection_name"]
    if len(relevant) != len(exa.input_columns) - 1:
        raise UdfParameterException(
            'UDF does not declare input column "connection_name".'
        )
    verify_columns(relevant, endpoint.input_columns)
    verify_columns(exa.output_columns, endpoint.output_columns)
