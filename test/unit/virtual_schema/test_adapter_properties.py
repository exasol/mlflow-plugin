from test.not_raises import not_raises

import pytest

from exasol.mlflow_plugin.virtual_schema.adapter_properties import (
    PropertiesError,
    Property,
    PropertyValidator,
)


@pytest.mark.parametrize(
    "type_, str_value, typed_value",
    [
        (str, None, None),
        (str, "", ""),
        (str, "abc", "abc"),
        (str, "123", "123"),
        (int, None, None),
        (int, "123", 123),
        (bool, None, None),
        (bool, "true", True),
        (bool, "True", True),
        (bool, "TRUE", True),
        (bool, "false", False),
        (bool, "FALSE", False),
        (bool, "False", False),
    ],
)
def test_property_validate_success(type_, str_value, typed_value):
    property = Property("P", type=type_)
    with not_raises(ValueError):
        property.validate(str_value)
    assert property.value(str_value) == typed_value


@pytest.mark.parametrize(
    "type_, value",
    [
        (int, "abc"),
        (int, ""),
        (bool, ""),
        (bool, "123"),
        (bool, "abc"),
    ],
)
def test_property_validate_failure(type_, value):
    property = Property("P", type=type_)
    with pytest.raises(PropertiesError):
        property.validate(value)


@pytest.mark.parametrize(
    "properties, values, message",
    [
        (None, {"A": "1"}, "1 unsupported property: A."),
        (None, {"A": "1", "B": "bb"}, "2 unsupported properties: A, B."),
        (
            [Property("a", int)],
            {"A": "1", "B": "bb"},
            "1 unsupported property: B.",
        ),
        (
            [Property("a", int)],
            {"A": "not a number"},
            'Illegal value "not a number" for Adapter Property "A"',
        ),
    ],
)
def test_validator_failure(properties, values, message) -> None:
    validator = PropertyValidator(properties)
    with pytest.raises(PropertiesError, match=message):
        validator.validate(values)


@pytest.mark.parametrize(
    "values",
    [
        pytest.param({"OTHER": "123"}, id="missing"),
        pytest.param({"REQUIRED": ""}, id="empty_string"),
        pytest.param({"REQUIRED": None}, id="null_value"),
    ]
)
def test_mandatory_properties(values) -> None:
    properties = [
        Property("required", str, mandatory=True),
        Property("other", int),
    ]
    validator = PropertyValidator(properties)
    with pytest.raises(
        PropertiesError,
        match="1 mandatory property is missing: REQUIRED.",
    ):
        validator.validate(values, check_mandatory=True)


@pytest.mark.parametrize(
    "properties, values",
    [
        ([], {}),
        ([Property("a", int)], {"A": "1"}),
        ([Property("a", int), Property("b", str)], {"A": "1"}),
    ],
)
def test_validator_success(properties, values) -> None:
    validator = PropertyValidator(properties)
    with not_raises(PropertiesError):
        validator.validate(values)
