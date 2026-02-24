import logging
from collections.abc import Callable
from test.integration.udfs import Udf

import mlflow
import pyexasol
import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector

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
) -> Callable[[str, str], Udf]:
    def create(name: str, impl: str) -> Udf:
        return Udf(
            pyexasol_connection, language_alias, db_schema_name, name, impl
        ).create()

    return create


def test_something_with_slc(create_udf):
    udf = create_udf(
        "LOAD_MLFLOW_MODEL",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}()
           RETURNS BOOLEAN AS
        def run(ctx):
            return True
        /
        """,
    )
    result = udf.run().fetchall()
    assert result[0][0] is True


@pytest.fixture
def connector_for_bfs_access(logged_sample_model):
    return Connector(
        logged_sample_model,
        username="not required",
        password="not required",
        ssl_cert_validation=False,
    )


def test_bfs_load_model(create_udf, logged_sample_model) -> None:
    udf = create_udf(
        "BFS_LOAD_MLFLOW_MODEL",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        import mlflow
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
        def run(ctx):
            con = Connector(ctx.uri, "", "", False)
            path = con.bucketfs_location.as_udf_path()
            model = mlflow.sklearn.load_model(path)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


def xtest_bfs2(connector_for_bfs_access) -> None:
    path = connector_for_bfs_access.bucketfs_location.as_udf_path()
    print(f"BucketFS Path: {path}")
    return
    loaded = mlflow.sklearn.load_model(path)


def test_http_load_model(
    create_udf,
    bucketfs_env_variables,
    logged_sample_model: str,
) -> None:
    udf = create_udf(
        "HTTP_LOAD_MLFLOW_MODEL",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        import mlflow
        import os
        from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD
        def run(ctx):
            os.environ[ENV_BUCKETFS_PASSWORD] = "not required"
            model = mlflow.sklearn.load_model(ctx.uri)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


def xtest_http2(bucketfs_env_variables, logged_sample_model) -> None:
    # This access method may need environment variables
    # such as BFS user (password not required) and SSL verification.
    model = mlflow.sklearn.load_model(logged_sample_model)
    cls = type(model)
    fqn = f"{cls.__module__}.{cls.__name__}"
    print(f"{fqn}")
