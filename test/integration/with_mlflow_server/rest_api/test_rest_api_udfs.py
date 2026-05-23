from exasol.mlflow_plugin.rest_api.experiments import ExperimentsSearch


def test_connection(mlflow_exa_connection, pyexasol_connection) -> None:
    result = pyexasol_connection.execute(
        "SELECT * from EXA_ALL_CONNECTIONS WHERE"
        f" CONNECTION_NAME='{mlflow_exa_connection}'"
    ).fetchall()
    assert len(result) == 1


# def test_x1():
#     cls = ExperimentsSearch
#     print(f'{cls.param_names}')
