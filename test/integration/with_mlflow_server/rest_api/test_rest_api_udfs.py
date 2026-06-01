import pytest

from exasol.mlflow_plugin import rest_api


def test_connection(mlflow_exa_connection, pyexasol_connection) -> None:
    result = pyexasol_connection.execute(
        "SELECT * from EXA_ALL_CONNECTIONS WHERE"
        f" CONNECTION_NAME='{mlflow_exa_connection}'"
    ).fetchall()
    assert len(result) == 1


@pytest.fixture(scope="session")
def rest_api_udfs(deployed_slc, db_schema_name, pyexasol_connection) -> None:
    language_alias = deployed_slc
    rest_api.udf.deployment.deploy_all(
        language_alias, db_schema_name, pyexasol_connection
    )


def test_experiments_search(
    deployed_slc, mlflow_exa_connection, db_schema_name, pyexasol_connection
) -> None:
    language_alias = deployed_slc
    cls = rest_api.ExperimentsSearch
    udf = rest_api.udf.deployment.Deployable(language_alias, db_schema_name, cls)
    udf.deploy(pyexasol_connection)
    sql = f"SELECT {udf.quoted_name}('{mlflow_exa_connection}', NULL, NULL, NULL, NULL)"
    actual = pyexasol_connection.execute(sql).fetchall()
    assert len(actual) > 0
