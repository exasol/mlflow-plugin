import logging
from collections.abc import Callable
from test.integration.udfs import (
    EnvSpec,
    Udf,
)

import pyexasol
import pytest

from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logging.getLogger("exasol.bucketfs").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def db_schema_name() -> str:
    return "ITEST_MLFLOW"


@pytest.fixture(scope="session")
def create_udf(
    deployed_slc: str,
    language_alias: str,
    pyexasol_connection: pyexasol.ExaConnection,
    db_schema_name: str,
) -> Callable[[str, str, EnvSpec], Udf]:
    def create(name: str, impl: str, env: EnvSpec = None) -> Udf:
        return Udf(
            pyexasol_connection, language_alias, db_schema_name, name, impl, env
        ).create()

    return create


def test_bfs_load_model(create_udf, logged_sample_model) -> None:
    udf = create_udf(
        "BFS_LOAD_MLFLOW_MODEL",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        import mlflow
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import udf_path
        def run(ctx):
            path = udf_path(ctx.uri)
            model = mlflow.sklearn.load_model(path)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


def test_http_load_model(create_udf, logged_sample_model: str) -> None:
    udf = create_udf(
        "HTTP_LOAD_MLFLOW_MODEL",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import mlflow
        def run(ctx):
            model = mlflow.sklearn.load_model(ctx.uri)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
        env={ENV_BUCKETFS_PASSWORD: "not required"},
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"
