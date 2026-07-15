import json
from test.unit.virtual_schema.property_utils import property_values
from unittest.mock import Mock

import pytest

from exasol.mlflow_plugin.virtual_schema import (
    AdapterProperties,
    RequestHandler,
)


@pytest.fixture
def adapter_properties() -> AdapterProperties:
    return AdapterProperties(["UNCHANGED", "VOLATILE"])


@pytest.fixture
def mocked_handler(adapter_properties):
    handler = RequestHandler(adapter_properties)
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


def test_properties_create(mocked_handler) -> None:
    request = {"type": "createVirtualSchema"} | property_values(
        {"VOLATILE": "initial value"}
    )
    mocked_handler.handle(json.dumps(request))
    actual = mocked_handler.create.call_args.args[1]
    assert actual == {"VOLATILE": "initial value"}


def test_properties_update(mocked_handler) -> None:
    request = {"type": "setProperties"} | property_values(
        {"UNCHANGED": "kept", "VOLATILE": "initial value"},
        {"VOLATILE": "new value"},
    )
    mocked_handler.handle(json.dumps(request))
    actual = mocked_handler.set_properties.call_args.args[1]
    assert actual == {"UNCHANGED": "kept", "VOLATILE": "new value"}
