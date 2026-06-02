from unittest.mock import Mock

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.udf.verification import (
    CONNECTION_NAME_PARAM,
    ExaMeta,
    ExaMetaColumn,
)


def mock_exa_object(endpoint: rest_api.Endpoint) -> Mock:
    def exa_meta_columns(columns: list[Column]) -> list[ExaMetaColumn]:
        return [ExaMetaColumn(c.sql_name, c.sql.split()[1]) for c in columns]

    mock = Mock()
    connection = Mock(address="address", user="user", password="password")
    mock.get_connection.return_value = connection

    em_input = exa_meta_columns([CONNECTION_NAME_PARAM] + endpoint.input_columns)
    em_output = exa_meta_columns(endpoint.total_output_columns)
    mock.meta = ExaMeta(em_input, em_output)

    return mock
