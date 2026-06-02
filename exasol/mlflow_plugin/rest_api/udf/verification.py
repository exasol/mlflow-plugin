from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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


CONNECTION_NAME_PARAM = Column.varchar("connection_name")


class Direction(Enum):
    INPUT = ("input", " (incl. connection name)", [CONNECTION_NAME_PARAM])
    OUTPUT = ("output", "", [])

    def __init__(self, label: str, comment: str, extra_columns: list[Column]):
        self.label = label
        self.comment = comment
        self.extra_columns = extra_columns


def verify_columns(
    direction: Direction, actual: list[ExaMetaColumn], expected: list[Column]
) -> None:
    """
    Verify if the UDF's actual list of columns as provided via exa.meta
    matches the list of expected columns as defined by the MLflow REST API
    endpoint.

    For direction "input" an UDF additional parameter connection_name is
    considered, specifiying the name of the connection for retrieving the REST
    API base URI and the credentials for authentication.
    """

    expected = direction.extra_columns + expected

    def suffix() -> str:
        actual_cols = ", ".join(f'"{c.name}" {c.sql_type.split()[0]}' for c in actual)
        expected_cols = ", ".join(c.sql for c in expected)
        return (
            f"* UDF declares {len(actual)} columns: {actual_cols}\n"
            f"* Endpoint expects {len(expected)} columns: {expected_cols}"
        )

    if len(actual) != len(expected):
        raise UdfParameterException(
            f"The number of {direction.label} columns declared for the UDF"
            f" doesn't match the MLflow REST API endpoint{direction.comment}.\n\n"
            f"{suffix()}"
        )

    expected_dict = {c.sql_name: c.sql_type for c in expected}
    for act in actual:
        exp = expected_dict.get(act.name)
        if act.sql_type.split()[0] != exp:
            raise UdfParameterException(
                f'UDF parameter "{act.name}"'
                " doesn't match the MLflow REST API endpoint parameters."
                f"\n\n{suffix()}"
            )


def verify_udf_parameters(exa_meta: ExaMeta, endpoint: Endpoint) -> None:
    """
    Raises UdfParameterException if the UDF's column declaration doesn't
    match the endpoint.
    """

    verify_columns(Direction.INPUT, exa_meta.input_columns, endpoint.input_columns)
    verify_columns(
        Direction.OUTPUT, exa_meta.output_columns, endpoint.total_output_columns
    )
