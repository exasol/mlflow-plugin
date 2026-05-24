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


def test_udf_body(exa_mock) -> None:
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

    # Simulate endpoint instance
    endpoint = Mock()
    simulated_rows = [["a", "b"], ["c", "d"]]
    endpoint.call.return_value = simulated_rows

    # Simulate endpoint class
    endpoint_cls = Mock(param_names=params, return_value=endpoint)

    # Simulate UDF ctx object
    ctx = mock_udf_ctx(params)
    ctx.connection_name = "CCC"

    # Instantiate and UDF body and call its run() method, just as the UDF would do
    body = rest_api.udf.Body(exa_mock, endpoint_cls)
    body.run(ctx)

    # Verify retrieval of exa connection
    assert exa_mock.get_connection.call_args == call(ctx.connection_name)
    # Verify constructor
    assert endpoint_cls.call_args == call("address", auth=("user", "password"))
    # Verify endpoint call
    assert endpoint.call.call_args == call(**params)
    # Verify emitted data
    assert ctx.emit.call_args_list == [call(*cols) for cols in simulated_rows]
