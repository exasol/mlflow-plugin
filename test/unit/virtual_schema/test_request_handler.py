import json
from unittest.mock import Mock

import pytest

from exasol.mlflow_plugin.virtual_schema import (
    RequestHandler,
)


@pytest.fixture
def mocked_handler():
    handler = RequestHandler()
    handler.create = Mock(return_value={})
    handler.refresh = Mock(return_value={})
    handler.drop = Mock(return_value={})
    handler.get_capabilities = Mock(return_value={})
    handler.set_properties = Mock(return_value={})
    handler.pushdown = Mock(return_value={})
    return handler


@pytest.mark.parametrize(
    "req_type, callback",
    [
        ("createVirtualSchema", "create"),
        ("setProperties", "set_properties"),
        ("createVirtualSchema", "create"),
        ("setProperties", "set_properties"),
        ("refresh", "refresh"),
        ("dropVirtualSchema", "drop"),
        ("getCapabilities", "get_capabilities"),
        ("pushdown", "pushdown"),
    ],
)
def test_callbacks(mocked_handler, req_type, callback) -> None:
    request = {"type": req_type}
    mocked_handler.handle(json.dumps(request))
    assert getattr(mocked_handler, callback).called
