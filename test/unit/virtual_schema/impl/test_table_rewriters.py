import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.vs_impl.rewrite_queries import TableRewriter
from exasol.mlflow_plugin.virtual_schema import JsonObject


def _request(fc_type: str, fc_name: str) -> JsonObject:
    return {
        "type": "pushdown",
        "pushdownRequest": {"from": {"type": fc_type, "name": fc_name}},
    }


@pytest.fixture
def rewriter() -> TableRewriter:
    return TableRewriter(rest_api.EXPERIMENTS_SEARCH, "EXPERIMENTS")


@pytest.mark.parametrize(
    "fc_type, fc_name, expected",
    [
        ("join", "any", False),
        ("table", "NOT_SUPPORTED", False),
        ("table", "EXPERIMENTS", True),
    ],
)
def test_can_handle(rewriter, fc_type, fc_name, expected) -> None:
    request = _request(fc_type, fc_name)
    assert rewriter.can_handle(request) == expected


@pytest.fixture
def sample_properties():
    return {"CONNECTION_NAME": "CCC", "MAX_RESULTS": "100"}


def test_rewrite(rewriter, sample_properties) -> None:
    request = _request("table", "EXPERIMENTS")
    actual = rewriter.rewrite(request, sample_properties, "UDF_SCHEMA")
    expected = (
        'SELECT "UDF_SCHEMA"."EXPERIMENTS_SEARCH"(' "'CCC', NULL, NULL, NULL, 100)"
    )
    assert actual == expected
