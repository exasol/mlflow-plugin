import pytest

from exasol.mlflow_plugin.exa_meta import ExaMeta
from exasol.mlflow_plugin.rest_api import vs_impl
from exasol.mlflow_plugin.rest_api.vs_impl.request_handler import udf_call
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PushdownError,
)


@pytest.fixture
def handler() -> vs_impl.RequestHandler:
    exa_meta = ExaMeta(
        input_columns=[], output_columns=[], script_schema="MLFLOW_REST_API"
    )
    return vs_impl.RequestHandler(exa_meta)


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
        pytest.param(
            {"type": "unsupported type"},
            "Unsupported pushdown type",
            id="unsupported_pushdown_type",
        ),
        pytest.param(
            {"type": "select", "selectList": SAMPLE_SELECT_LIST},
            "Unsupported selectList",
            id="unsupported_selectlist",
        ),
        pytest.param(
            {"type": "select", "from": {"type": "join"}},
            "Unsupported FROM type",
            id="unsupported_from_type",
        ),
    ],
)
def test_pushdown_error(pushdown_details, handler, expected_error) -> None:
    request = _request("pushdown") | {"pushdownRequest": pushdown_details}
    with pytest.raises(PushdownError, match=expected_error):
        handler.pushdown(request)


def test_pushdown_success(handler) -> None:
    pushdown_details = {
        "pushdownRequest": {"type": "select", "from": {"type": "table"}}
    }
    request = _request("pushdown") | pushdown_details
    actual = handler.pushdown(request)
    assert actual["type"] == request["type"]
    assert "sql" in actual


def test_udf_call():
    actual = udf_call("schema", "connection", "EXPERIMENTS")
    assert actual == (
        'SELECT "schema"."EXPERIMENTS_SEARCH"'  #
        "('connection', NULL, NULL, NULL, NULL)"
    )
