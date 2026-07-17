from test.not_raises import not_raises

import pytest

from exasol.mlflow_plugin.virtual_schema import (
    AdapterProperties,
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
