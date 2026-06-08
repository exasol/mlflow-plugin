import pytest

from exasol.mlflow_plugin.rest_api import expanding
from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


@pytest.mark.parametrize(
    "element, expected",
    [
        pytest.param({"a": 1}, [{}], id="default_value"),
        pytest.param({"a": 1, "b": {}}, [{}], id="not_found_level_2"),
        pytest.param({"a": 1, "b": {"c": 2}}, [2], id="found"),
    ],
)
def test_nested(element, expected) -> None:
    locator = ["b", "c"]
    actual = expanding._nested(element, locator)
    assert actual == expected


@pytest.fixture
def sample_expander(locator: list[str] | None = None) -> expanding.Expander:
    return expanding.Expander(
        locator=locator or ["b", "c"],
        output=[
            Column("c1", 10),
            Column("c2", 10),
        ],
    )


def test_child_not_found(sample_expander) -> None:
    actual = list(sample_expander.expand([{}]))
    assert actual == [{"c1": None, "c2": None}]


def input_data(value: JsonObject | list[JsonObject]) -> JsonObject:
    return {
        "a": "a value",
        "b": {
            "c": value,
        },
    }


def test_expand_scalar(sample_expander) -> None:
    """
    Input data contains a nested object.  Verify Expander to extract and
    add the nested values as top-level output.
    """

    value = {"c1": "v1", "c2": "v2"}
    data = input_data(value)
    actual = list(sample_expander.expand([data]))
    assert actual == [data | value]


def test_expand_array(sample_expander) -> None:
    """
    Input data contains a nested object with an array value.  Verify
    Expander to repeat the input data for each array element, extract and add
    the nested values as top-level output.
    """

    value = [
        {"c1": "v1", "c2": "v2"},
        {"c1": "v3", "c2": "v4"},
    ]
    data = input_data(value)
    actual = list(sample_expander.expand([data]))
    expected = [
        data | value[0],
        data | value[1],
    ]
    assert actual == expected
