import pytest

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
    assert len(actual["schemaMetadata"]["tables"]) == 8


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


SAMPLE_SELECT_LIST = [{"columnNr": 0, "name": "ID", "tableName": "A", "type": "column"}]


@pytest.mark.parametrize(
    "pushdown_details, expected_error",
    [
        ({"type": "unsupported type"}, "Unsupported type"),
        (
            {"type": "select", "selectList": SAMPLE_SELECT_LIST},
            "Unsupported selectList",
        ),
    ],
)
def test_pushdown_error(pushdown_details, handler, expected_error) -> None:
    request = _request("pushdown") | {"pushdownRequest": pushdown_details}
    with pytest.raises(PushdownError, match=expected_error):
        handler.pushdown(request)


def test_pushdown_success(handler) -> None:
    request = _request("pushdown") | {"pushdownRequest": {"type": "select"}}
    actual = handler.pushdown(request)
    assert actual["type"] == request["type"]
    assert "sql" in actual
