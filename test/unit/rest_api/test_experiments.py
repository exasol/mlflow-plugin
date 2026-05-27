from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin import rest_api


@pytest.fixture
def rest_api_mock(monkeypatch):
    mock = Mock()
    mock.call.return_value = []
    monkeypatch.setattr(rest_api.rest_api, "MLflowRestApi", Mock(return_value=mock))
    return mock


def test_call_parameters(rest_api_mock) -> None:
    """
    Verify

    * Parameters with value None are removed
    * Parameters with resp. Column having attribute comma_sep=True are split
      into arrays.
    """
    testee = rest_api.ExperimentsSearch("base_uri")
    testee.call(
        filter=None,
        view_type="vt",
        order_by="a DESC,b ASC",
        max_results=20,
    )
    expected = {
        "view_type": "vt",
        "order_by": ["a DESC", "b ASC"],
        "max_results": 20,
    }
    assert rest_api_mock.call.call_args == call(expected)
