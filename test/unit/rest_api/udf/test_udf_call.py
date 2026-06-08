from test.unit.rest_api.udf.mocking import mock_exa_object
from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

import exasol.mlflow_plugin.rest_api.udf.call as udf_call
from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import JsonObject


def mock_udf_ctx(args: dict[str, Any]) -> Mock:
    ctx = Mock(**args)
    ctx.__getitem__ = lambda self, y: getattr(self, y)
    return ctx


@pytest.fixture
def sample_endpoint() -> rest_api.Endpoint:
    return rest_api.EXPERIMENTS_SEARCH


@pytest.fixture
def sample_params() -> JsonObject:
    return {
        "filter": "filter",
        "view_type": "DELETED",
        "order_by": "name,experiment_id",
        "max_results": 20,
    }


@pytest.fixture
def ctx_mock(sample_params) -> Mock:
    ctx = mock_udf_ctx(sample_params)
    ctx.connection_name = "CCC"
    return ctx


@pytest.mark.parametrize("user", [
    {}, {"auth-type": "unsupported"}
])
def test_unsupported_authentication(monkeypatch, sample_endpoint, ctx_mock, user) -> None:
    """
    Argument ``user`` contains the simulated value of the attribute
    ``user`` of an Exasol Connection.
    """
    exa = mock_exa_object(sample_endpoint, user=user)
    testee = rest_api.UdfCall(exa, sample_endpoint)
    with pytest.raises(NotImplementedError):
        testee.run(ctx_mock)


def test_udf_call(monkeypatch, ctx_mock, sample_params, sample_endpoint) -> None:
    """
    Verify the generic UdfCall class used by all UDFs for accessing the
    MLflow REST API.
    """

    # Simulate data_stream class
    data_stream = Mock()
    simulated_rows = [["a", "b"], ["c", "d"]]
    data_stream.retrieve.return_value = simulated_rows
    data_stream_cls = Mock(return_value=data_stream)
    monkeypatch.setattr(udf_call, "DataStream", data_stream_cls)

    # Mock exa object incl. the UDF's parameter declarations
    exa_mock = mock_exa_object(sample_endpoint)

    # Instantiate a UdfCall and call its run() method, just as the UDF would do
    testee = rest_api.UdfCall(exa_mock, sample_endpoint)
    testee.run(ctx_mock)

    # Verify retrieval of exa connection
    assert exa_mock.get_connection.call_args == call(ctx_mock.connection_name)

    # Verify constructor
    assert data_stream_cls.call_args == call(
        base_uri="address",
        auth=("user", "password"),
        endpoint=sample_endpoint,
    )

    # Verify endpoint call
    expected_params = sample_params | {"order_by": ["name", "experiment_id"]}
    assert data_stream.retrieve.call_args == call(expected_params)

    # Verify emitted data
    assert ctx_mock.emit.call_args_list == [call(*cols) for cols in simulated_rows]
