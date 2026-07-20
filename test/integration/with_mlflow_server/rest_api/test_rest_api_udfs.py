import exasol.mlflow_plugin.rest_api.udf.deployment as udf_deployment
from exasol.mlflow_plugin import rest_api


def test_connection(mlflow_exa_connection, pyexasol_connection) -> None:
    result = pyexasol_connection.execute(
        "SELECT * from EXA_ALL_CONNECTIONS WHERE"
        f" CONNECTION_NAME='{mlflow_exa_connection}'"
    ).fetchall()
    assert len(result) == 1


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
    print(f"{actual}")
    assert len(actual) > 0
