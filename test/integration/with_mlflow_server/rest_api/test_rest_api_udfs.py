import pytest

from exasol.mlflow_plugin import rest_api


def test_connection(mlflow_exa_connection, pyexasol_connection) -> None:
    result = pyexasol_connection.execute(
        "SELECT * from EXA_ALL_CONNECTIONS WHERE"
        f" CONNECTION_NAME='{mlflow_exa_connection}'"
    ).fetchall()
    assert len(result) == 1


@pytest.fixture(scope="session")
def rest_api_udfs(language_alias, db_schema_name, pyexasol_connection) -> None:
    rest_api.udf.deploy_all(
        language_alias=language_alias,
        schema=db_schema_name,
        pyexasol_connection,
    )


def test_x1(
    language_alias, mlflow_exa_connection, db_schema_name, pyexasol_connection
) -> None:
    cls = rest_api.ExperimentsSearch
    udf = rest_api.udf.Deployable(language_alias, db_schema_name, cls)
    udf.deploy(pyexasol_connection)
    sql = f"SELECT {udf.quoted_name}('{mlflow_exa_connection}', NULL, NULL, NULL, NULL)"
    actual = pyexasol_connection.execute(sql).fetchall()
    assert len(actual) > 0
