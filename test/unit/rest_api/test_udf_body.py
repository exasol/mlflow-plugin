from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin import rest_api


@pytest.fixture
def connection_mock():
    return Mock(address="address", user="user", password="password")


@pytest.fixture
def exa_mock(connection_mock):
    mock = Mock()
    mock.get_connection.return_value = connection_mock
    return mock


def mock_udf_ctx(args: dict[str, Any]) -> Mock:
    ctx = Mock(**args)
    ctx.__getitem__ = lambda self, y: getattr(self, y)
    return ctx


def test_udf_body(monkeypatch, exa_mock) -> None:
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
    monkeypatch.setattr(rest_api.udf_body, "ApiAdapter", adapter_cls)

    # Simulate UDF ctx object
    ctx = mock_udf_ctx(params)
    ctx.connection_name = "CCC"

    # Instantiate a UDF body and call its run() method, just as the UDF would do
    endpoint = rest_api.EXPERIMENTS_SEARCH
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
