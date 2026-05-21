from exasol.mlflow_plugin.rest_api.column import Column
from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.expanding import EXPAND_TAGS
from exasol.mlflow_plugin.rest_api.processing import PostProcessor


def test_no_expansion() -> None:
    testee = PostProcessor(
        columns=[
            Column("c1", 10),
            Column("c2", 10),
        ],
    )
    input = [
        {"c1": 1, "c2": 2},
        {"c1": 3, "c2": 4},
    ]
    actual = list(testee.process(input))
    assert actual == [[1, 2], [3, 4]]


def test_expansion() -> None:
    testee = PostProcessor(columns=[Column("c1", 10)], expanders=[EXPAND_TAGS])
    tags = [
        {"key": "K1", "value": "V1"},
        {"key": "K2", "value": "V2"},
    ]
    input: list[JsonObject] = [{"c1": 1, "tags": tags}, {"c1": 2}]
    actual = list(testee.process(input))
    assert actual == [
        [1, "K1", "V1"],
        [1, "K2", "V2"],
        [2, None, None],
    ]
