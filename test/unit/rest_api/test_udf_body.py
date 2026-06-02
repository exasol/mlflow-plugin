import contextlib
from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api import adapter
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.udf import body as udf_body
from exasol.mlflow_plugin.rest_api.udf.verification import (
    ExaMeta,
    ExaMetaColumn,
    UdfParameterException,
    verify_columns,
)


@pytest.fixture
def connection_mock():
    return Mock(address="address", user="user", password="password")


def mock_udf_ctx(args: dict[str, Any]) -> Mock:
    ctx = Mock(**args)
    ctx.__getitem__ = lambda self, y: getattr(self, y)
    return ctx


@pytest.mark.parametrize("actual, expected", [
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL(18,0)"), ExaMetaColumn("b", "DECIMAL(18,0)")],
        [Column.decimal("a")],
        id="2_actual_1_expected",
    ),
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL(18,0)")],
        [Column.decimal("a"), Column.decimal("b")],
        id="1_actual_2_expected",
    ),
    pytest.param(
        [ExaMetaColumn("a", "VARCHAR(200)")],
        [Column.varchar("b", 200)],
        id="name_mismatch",
    ),
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL")],
        [Column.varchar("a", 200)],
        id="decimal_varchar",
    ),
    pytest.param(
        [ExaMetaColumn("a", "VARCHAR(200)")],
        [Column.decimal("a")],
        id="varchar_decimal",
    ),
    pytest.param(
        [ExaMetaColumn("a", "VARCHAR(200)")],
        [Column.varchar("a", 201)],
        id="size",
    ),
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL(18,0)")],
        [Column.decimal("a", 17)],
        id="precision",
    ),
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL(10,2)")],
        [Column.decimal("a", 10)],
        id="scale",
    ),
])
def test_verify_input_columns_fails(actual, expected) -> None:
    with pytest.raises(UdfParameterException):
        verify_columns(actual, expected)


@contextlib.contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"Did raise {exception}")


@pytest.mark.parametrize("actual, expected", [
    pytest.param(
        [ExaMetaColumn("a", "DECIMAL(18,0)")],
        [Column.decimal("a")],
        id="decimal",
    ),
    pytest.param(
        [ExaMetaColumn("a", "VARCHAR(200)")],
        [Column.varchar("a", 200)],
        id="varchar",
    ),
    pytest.param(
        [ExaMetaColumn("a", "VARCHAR(200)"), ExaMetaColumn("b", "DECIMAL(10,0)")],
        [Column.varchar("a", 200), Column.decimal("b", 10)],
        id="2-columns",
    ),
])
def test_verify_input_columns_succeeds(actual, expected) -> None:
    with not_raises(UdfParameterException):
        verify_columns(actual, expected)


def mock_exa_object(
    connection: Mock,
    input_columns: list[Column],
    output_columns: list[Column],
) -> Mock:
    def exa_meta_columns(columns: list[Column]) -> list[ExaMetaColumn]:
        return [ExaMetaColumn(c.sql_name, c.sql.split()[1]) for c in columns]

    mock = Mock()
    mock.get_connection.return_value = connection

    connection_param = Column.varchar("connection_name")
    em_input = exa_meta_columns([connection_param] + input_columns)
    em_output = exa_meta_columns(output_columns)
    mock.meta = ExaMeta(em_input, em_output)

    return mock


def test_udf_body(monkeypatch, connection_mock) -> None:
    """
    Verify the generic Body class used by all UDFs for accessing the
    MLflow REST API.
    """

    params = {
        "filter": "filter",
        "view_type": "DELETED",
        "order_by": "name,experiment_id",
        "max_results": 20,
    }

    # Simulate adapter class
    api_adapter = Mock()
    simulated_rows = [["a", "b"], ["c", "d"]]
    api_adapter.call.return_value = simulated_rows
    adapter_cls = Mock(return_value=api_adapter)
    monkeypatch.setattr(udf_body, "ApiAdapter", adapter_cls)

    # Simulate UDF ctx object
    ctx = mock_udf_ctx(params)
    ctx.connection_name = "CCC"

    endpoint = rest_api.EXPERIMENTS_SEARCH

    # Mock exa object incl. the UDF's parameter declarations
    exa_mock = mock_exa_object(connection_mock, endpoint.input_columns, endpoint.output_columns)

    # Instantiate a UDF body and call its run() method, just as the UDF would do
    body = rest_api.UdfBody(exa_mock, endpoint)
    body.run(ctx)

    # Verify retrieval of exa connection
    assert exa_mock.get_connection.call_args == call(ctx.connection_name)

    # Verify constructor
    assert adapter_cls.call_args == call(
        base_uri="address",
        auth=("user", "password"),
        endpoint=endpoint,
    )

    # Verify endpoint call
    expected_params = params | {"order_by": ["name", "experiment_id"]}
    assert api_adapter.call.call_args == call(expected_params)

    # Verify emitted data
    assert ctx.emit.call_args_list == [call(*cols) for cols in simulated_rows]
