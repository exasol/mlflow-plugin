from inspect import cleandoc

import pytest

from exasol.mlflow_plugin.exa_meta import ExaMeta
from exasol.mlflow_plugin.rest_api import vs_impl
from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PropertiesDict,
    PropertiesError,
    PushdownError,
)


@pytest.fixture
def utest_schema():
    return "UTEST_MLFLOW"


@pytest.fixture
def handler(utest_schema) -> vs_impl.RequestHandler:
    exa_meta = ExaMeta(input_columns=[], output_columns=[], script_schema=utest_schema)
    return vs_impl.RequestHandler(exa_meta)


def _request(_type: str) -> JsonObject:
    return {"type": _type}


def test_create_success(handler) -> None:
    request = _request("createVirtualSchema") | {
        "schemaMetadataInfo": {"properties": {"CONNECTION_NAME": "CCC"}}
    }
    actual = handler.create(request)
    assert actual["type"] == request["type"]
    assert len(actual["schemaMetadata"]["tables"]) == len(vs_impl.REWRITERS)


MISSING_CONNECTION_NAME = "1 mandatory property is missing: CONNECTION_NAME."


@pytest.mark.parametrize(
    "properties, expected_error",
    [
        ({}, MISSING_CONNECTION_NAME),
        ({"CONNECTION_NAME": None}, MISSING_CONNECTION_NAME),
        ({"CONNECTION_NAME": ""}, MISSING_CONNECTION_NAME),
        (
            {
                "CONNECTION_NAME": "AAA",
                "MAX_RESULTS": "not-a-number",
            },
            'Illegal value "not-a-number" for Adapter Property "MAX_RESULTS".',
        ),
    ],
)
def test_property_error_in_create(handler, properties, expected_error) -> None:
    request = _request("createVirtualSchema") | {
        "schemaMetadataInfo": {"properties": properties}
    }
    with pytest.raises(PropertiesError, match=expected_error):
        handler.create(request)


def _set_properties_request(properties: PropertiesDict) -> PropertiesDict:
    return _request("setProperties") | {
        "schemaMetadataInfo": {"properties": {"CONNECTION_NAME": "CCC"}},
        "properties": properties,
    }


@pytest.mark.parametrize(
    "properties",
    [
        pytest.param({}, id="empty"),
        pytest.param({"CONNECTION_NAME": "altered"}, id="updated"),
    ],
)
def test_set_properties_success(handler, properties) -> None:
    request = _set_properties_request(properties)
    actual = handler.set_properties(request)
    assert actual["type"] == request["type"]


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty_string"),
        pytest.param(None, id="null_value"),
    ],
)
def test_set_properties_failure(handler, value) -> None:
    request = _set_properties_request({"CONNECTION_NAME": value})
    with pytest.raises(PropertiesError, match="mandatory property is missing"):
        handler.set_properties(request)


@pytest.mark.parametrize(
    "method_name, expected",
    [
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
            "Unsupported Pushdown from clause",
            id="unsupported_from_type",
        ),
        pytest.param(
            {"type": "select", "from": {"type": "table", "name": "UNKNOWN"}},
            "Unsupported Pushdown from clause",
            id="unsupported_table",
        ),
    ],
)
def test_pushdown_error(pushdown_details, handler, expected_error) -> None:
    request = _request("pushdown") | {"pushdownRequest": pushdown_details}
    with pytest.raises(PushdownError, match=expected_error):
        handler.pushdown(request)


def pushdown_for_vs_table(table_name: str):
    pushdown_details = {
        "pushdownRequest": {
            "type": "select",
            "from": {"type": "table", "name": table_name},
        },
        "schemaMetadataInfo": {"properties": {"MAX_RESULTS": "123"}},
    }
    return _request("pushdown") | pushdown_details


def test_pushdown_success(handler, utest_schema) -> None:
    request = pushdown_for_vs_table("EXPERIMENTS")
    actual = handler.pushdown(request)
    expected_sql = (
        f'SELECT "{utest_schema}"."EXPERIMENTS_SEARCH"('
        "'MLFLOW', NULL, NULL, NULL, 123)"
    )
    assert actual == {"type": "pushdown", "sql": expected_sql}


def test_pushdown_to_table_rewriter_with_sub_query(handler, utest_schema) -> None:
    request = pushdown_for_vs_table("RUNS")
    actual = handler.pushdown(request)
    expected = cleandoc(f"""
        SELECT "{utest_schema}"."RUNS_SEARCH"(
            'MLFLOW', AUX."experiment_id", NULL, NULL, NULL, 123
        ) FROM (
            SELECT "{utest_schema}"."EXPERIMENTS_SEARCH"(
                'MLFLOW', NULL, NULL, NULL, 123
            )
        ) AUX
    """)
    assert actual["sql"] == expected
