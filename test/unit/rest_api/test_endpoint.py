import pytest

from exasol.mlflow_plugin import rest_api


def cut_suffixes(value: str, suffixes: list[str]):
    for s in suffixes:
        if value.endswith(s):
            return value[: -len(s)]
    return value


@pytest.mark.parametrize("endpoint", rest_api.ALL_ENDPOINTS)
def test_virtual_schema_table(endpoint) -> None:
    var_name = endpoint.var_name
    expected = cut_suffixes(endpoint.var_name, ["_LIST", "_SEARCH", "S_GET", "_GET"])
    assert endpoint.virtual_schema_table == expected
