import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api import vs_impl
from exasol.mlflow_plugin.virtual_schema import (
    AdapterProperties,
    JsonObject,
    PushdownError,
)


@pytest.fixture
def handler() -> vs_impl.RequestHandler:
    properties = AdapterProperties(["CONNECTION_NAME", "MAX_RESULTS"])
    return vs_impl.RequestHandler(properties)


def _request(_type: str) -> JsonObject:
    return {"type": _type}


def test_create(handler) -> None:
    request = _request("createVirtualSchema")
    actual = handler.create(request)
    assert actual["type"] == request["type"]
    assert len(actual["schemaMetadata"]["tables"]) == len(rest_api.ALL_ENDPOINTS)


@pytest.mark.parametrize(
    "method_name, expected",
    [
        ("set_properties", {}),
        ("refresh", {}),
        ("drop", {}),
        ("get_capabilities", {"capabilities": []}),
    ],
)
def test_other_methods(handler, method_name, expected) -> None:
    request = _request("setProperties")
    method = getattr(handler, method_name)
    actual = method(request)
    assert actual == request | expected


@pytest.mark.parametrize(
    "pushdown_details",
    [
        {"type": "unsupported type"},
        {"selectList": []},
    ],
)
def test_pushdown_error(pushdown_details, handler) -> None:
    request = _request("pushdown") | {"pushdownRequest": pushdown_details}
    with pytest.raises(PushdownError):
        handler.pushdown(request)


def test_pushdown_success(handler) -> None:
    request = _request("pushdown") | {"pushdownRequest": {"type": "select"}}
    actual = handler.pushdown(request)
    assert actual["type"] == request["type"]
    assert "sql" in actual
