from __future__ import annotations

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


CONNECTION_NAME_PARAM = Column.varchar("connection_name")


def verify_columns(
    direction: str, actual: list[ExaMetaColumn], expected: list[Column]
) -> None:
    if direction == "input":
        expected = [CONNECTION_NAME_PARAM] + expected
        comment = " (incl. connection name)"
    else:
        comment = ""

    def suffix() -> str:
        actual_cols = ", ".join(f'"{c.name}" {c.sql_type.split()[0]}' for c in actual)
        expected_cols = ", ".join(c.sql for c in expected)
        return (
            f"* UDF declares {len(actual)} columns: {actual_cols}\n"
            f"* Endpoint expects {len(expected)} columns: {expected_cols}"
        )

    if len(actual) != len(expected):
        raise UdfParameterException(
            f"The number of {direction} columns declared for the UDF"
            f" doesn't match the MLflow REST API endpoint{comment}.\n\n"
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
    verify_columns("input", exa_meta.input_columns, endpoint.input_columns)
    verify_columns("output", exa_meta.output_columns, endpoint.total_output_columns)
