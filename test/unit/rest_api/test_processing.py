from exasol.mlflow_plugin.rest_api.column import Column
from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.processing import PostProcessor


def test_no_expansion() -> None:
    testee = PostProcessor(
        has_tags=False,
        columns=[
            Column("c1", 10),
            Column("c2", 10),
        ],
    )
    input = [
        {"c1": 1, "c2": 2},
        {"c1": 3, "c2": 4},
    ]
    assert list(testee.process(input)) == [[1, 2], [3, 4]]


def test_expansion() -> None:
    testee = PostProcessor(has_tags=True, columns=[Column("c1", 10)])
    tags = [
        {"key": "K1", "value": "V1"},
        {"key": "K2", "value": "V2"},
    ]
    input: list[JsonObject] = [{"c1": 1, "tags": tags}, {"c1": 2}]
    assert list(testee.process(input)) == [
        [1, "K1", "V1"],
        [1, "K2", "V2"],
        [2, None, None],
    ]
