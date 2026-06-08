import json
from datetime import datetime
from unittest.mock import Mock

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)
from exasol.mlflow_plugin.rest_api.udf.verification import (
    CONNECTION_NAME_PARAM,
    ExaMeta,
    ExaMetaColumn,
)


def exa_meta_column(column: Column) -> ExaMetaColumn:
    name = column.sql_name
    if column.data_type == str:
        return ExaMetaColumn.varchar(name, column.size)
    if column.data_type == int:
        return ExaMetaColumn.decimal(name, column.size, 0)
    if column.data_type == datetime:
        return ExaMetaColumn.timestamp(name)
    if column.data_type == bool:
        return ExaMetaColumn.boolean(name)
    raise RuntimeError(f"Unexpected data_type: {column}")


DEFAULT_USER = {"auth-type": "basic", "user": "user"}
DEFAULT_PASSWORD = {"password": "password"}


def mock_exa_object(
    endpoint: rest_api.Endpoint,
    user: JsonObject = DEFAULT_USER,
    password: JsonObject = DEFAULT_PASSWORD,
) -> Mock:
    def exa_meta_columns(columns: list[Column]) -> list[ExaMetaColumn]:
        return [exa_meta_column(c) for c in columns]

    mock = Mock()
    connection = Mock(
        address="address",
        user=json.dumps(user),
        password=json.dumps(password),
    )
    mock.get_connection.return_value = connection

    em_input = exa_meta_columns([CONNECTION_NAME_PARAM] + endpoint.input_columns)
    em_output = exa_meta_columns(endpoint.total_output_columns)
    mock.meta = ExaMeta(em_input, em_output)

    return mock
