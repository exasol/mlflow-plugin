from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint


class UdfParameterException(Exception):
    """UDF parameter desclaration doesn't match the endpoint columns"""


@dataclass
class ExaMetaColumn:
    name: str
    sql_type: str
    type: type
    length: int
    precision: int
    scale: int

    @classmethod
    def boolean(cls, name: str) -> ExaMetaColumn:
        return cls(name, "BOOLEAN", bool, 0, 0, 0)

    @classmethod
    def timestamp(cls, name: str) -> ExaMetaColumn:
        return cls(name, "TIMESTAMP(3)", datetime, 0, 0, 0)

    @classmethod
    def decimal(cls, name: str, precision: int = 18, scale: int = 0) -> ExaMetaColumn:
        return cls(name, f"DECIMAL({precision},{scale})", int, 0, precision, scale)

    @classmethod
    def varchar(cls, name: str, length: int = 2000000) -> ExaMetaColumn:
        return cls(name, f"VARCHAR({length})", str, length, 0, 0)


@dataclass
class ExaMeta:
    input_columns: list[ExaMetaColumn]
    output_columns: list[ExaMetaColumn]


CONNECTION_NAME_PARAM = Column.varchar("connection_name")


class Direction(Enum):
    """
    This enum represents the direction of columns to verify: Either INPUT
    or OUTPUT.

    Each enum entry contains a label, a comment, and a list of extra columns.

    The label and comment are used when creating the error message in case the
    verification fails.

    The extra_column CONNECTION_NAME_PARAM is added for Direction.INPUT to
    accept an additional input parameter that is not declared by the endpoint
    but required to ispecifiy the name of the connection for retrieving the
    REST API base URI and the credentials for authentication.
    """

    INPUT = ("input", " (incl. connection name)", [CONNECTION_NAME_PARAM])  # type: ignore
    OUTPUT = ("output", "", [])  # type: ignore

    def __init__(self, label: str, comment: str, extra_columns: list[Column]):
        self.label = label
        self.comment = comment
        self.extra_columns = extra_columns


def matches(exa: ExaMetaColumn, col: Column | None) -> bool:
    """
    Check if the specified ExaMetaColumn matches the Column as used for
    this REST API implementation.

    See
    * https://docs.exasol.com/db/latest/database_concepts/udf_scripts/python3.htm#Input/ou
    * https://github.com/exasol/script-languages/blob/master/exaudfclient/base/
      python/exascript_python_preset_core.py#L101C18-L101C36
    """

    if col is None or exa.type != col.data_type:
        return False

    if exa.type in [datetime, bool]:
        return True
    if exa.type == str:
        return exa.length == col.size
    if exa.type == int:
        return exa.precision == col.size and exa.scale == 0
    return False


def verify_columns(
    direction: Direction, actual: list[ExaMetaColumn], expected: list[Column]
) -> None:
    """
    Verify if the UDF's actual list of columns as provided via exa.meta
    matches the list of expected columns as defined by the MLflow REST API
    endpoint.
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

    expected_dict = {c.sql_name: c for c in expected}
    for act in actual:
        exp = expected_dict.get(act.name)
        if not matches(act, exp):
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
