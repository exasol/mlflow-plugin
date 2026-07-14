from test.not_raises import not_raises

import pytest

from exasol.mlflow_plugin.rest_api.virtual_schema import (
    AdapterProperties,
    JsonObject,
    PropertiesDict,
    PropertiesError,
)


@pytest.mark.parametrize(
    "properties, values, message",
    [
        (None, {"A": "1"}, "1 unsupported property: A."),
        (None, {"A": "1", "B": "bb"}, "2 unsupported properties: A, B."),
        (["a"], {"A": "1", "B": "bb"}, "1 unsupported property: B."),
    ],
)
def test_validate_failure(properties, values, message) -> None:
    testee = AdapterProperties(properties)
    with pytest.raises(PropertiesError, match=message):
        testee.validate(values)


@pytest.mark.parametrize(
    "properties, values",
    [
        (None, {}),
        (["a"], {"A": "1"}),
        (["a", "b"], {"A": "1"}),
    ],
)
def test_validate_success(properties, values) -> None:
    testee = AdapterProperties(properties)
    with not_raises(PropertiesError):
        testee.validate(values)


@pytest.fixture
def adapter_properties() -> AdapterProperties:
    return AdapterProperties(["A", "B"])


def _property_values(
    initial: PropertiesDict, update: PropertiesDict | None = None
) -> JsonObject:
    return {
        "schemaMetadataInfo": {"properties": initial},
        "properties": update or {},
    }


@pytest.mark.parametrize(
    "_request, expected",
    [
        ({}, {}),
        ({"schemaMetadataInfo": {}}, {}),
        (_property_values({}), {}),
        (_property_values({"A": "1"}), {"A": "1"}),
        (_property_values({"A": "1", "B": "2"}), {"A": "1", "B": "2"}),
    ],
)
def test_initial_values(adapter_properties, _request, expected) -> None:
    assert adapter_properties.initial(_request) == expected


def test_initial_illegal_value(adapter_properties) -> None:
    request = _property_values({"ILLEGAL": "c"})
    with pytest.raises(PropertiesError):
        adapter_properties.initial(request)


@pytest.mark.parametrize(
    "_request, expected",
    [
        pytest.param(_property_values({}, {}), {}, id="empty"),
        pytest.param(_property_values({"A": "1"}, {}), {"A": "1"}, id="unchanged"),
        pytest.param(
            _property_values({"A": "1"}, {"A": "2"}), {"A": "2"}, id="updated"
        ),
        pytest.param(
            _property_values({"A": "1"}, {"B": "2"}), {"A": "1", "B": "2"}, id="added_b"
        ),
        pytest.param(
            _property_values({"A": "1", "B": "2"}, {"A": "2"}),
            {"A": "2", "B": "2"},
            id="updated_a",
        ),
        pytest.param(
            _property_values({"A": "1", "B": "2"}, {"A": None}),
            {"B": "2"},
            id="unset_a",
        ),
    ],
)
def test_update(adapter_properties, _request, expected) -> None:
    assert adapter_properties.update(_request) == expected


def test_update_illegal_value(adapter_properties) -> None:
    request = _property_values({}, {"ILLEGAL": "value"})
    with pytest.raises(PropertiesError):
        adapter_properties.update(request)
