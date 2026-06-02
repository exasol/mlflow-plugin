import pytest

from exasol.mlflow_plugin import rest_api
import exasol.mlflow_plugin.rest_api.udf.deployment as udf_deployment


def test_connection(mlflow_exa_connection, pyexasol_connection) -> None:
    result = pyexasol_connection.execute(
        "SELECT * from EXA_ALL_CONNECTIONS WHERE"
        f" CONNECTION_NAME='{mlflow_exa_connection}'"
    ).fetchall()
    assert len(result) == 1


@pytest.fixture(scope="session")
def rest_api_udfs(deployed_slc, db_schema_name, pyexasol_connection) -> None:
    language_alias = deployed_slc
    udf_deployment.deploy_all(language_alias, db_schema_name, pyexasol_connection)


def test_experiments_search(
    deployed_slc, mlflow_exa_connection, db_schema_name, pyexasol_connection
) -> None:
    language_alias = deployed_slc
    udf = udf_deployment.Deployable(
        language_alias,
        db_schema_name,
        rest_api.EXPERIMENTS_SEARCH,
    )
    udf.deploy(pyexasol_connection)
    sql = f"SELECT {udf.quoted_name}('{mlflow_exa_connection}', NULL, NULL, NULL, NULL)"
    actual = pyexasol_connection.execute(sql).fetchall()
    assert len(actual) > 0
