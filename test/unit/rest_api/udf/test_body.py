from test.unit.rest_api.udf.mocking import mock_exa_object
from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.udf import body as udf_body


@pytest.fixture
def connection_mock():
    return Mock(address="address", user="user", password="password")


def mock_udf_ctx(args: dict[str, Any]) -> Mock:
    ctx = Mock(**args)
    ctx.__getitem__ = lambda self, y: getattr(self, y)
    return ctx


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
    exa_mock = mock_exa_object(endpoint)

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
