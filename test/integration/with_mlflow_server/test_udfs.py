import logging
from collections.abc import Callable
from test.integration.with_mlflow_server.udfs import (
    EnvSpec,
    Udf,
)

import pyexasol
import pytest

from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logging.getLogger("exasol.bucketfs").setLevel(logging.WARNING)
logging.getLogger("test.integration.with_mlflow_server.udfs").setLevel(logging.DEBUG)


SKLEARN_PACKAGE = "sklearn.linear_model._logistic.LogisticRegression"


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
        env = env or {}
        sql = f"""
        --/
        CREATE OR REPLACE {{language_alias!r}} SCALAR SCRIPT
            {{schema!q}}.{{name!q}}(uri VARCHAR(2000))
            RETURNS VARCHAR(2000) AS
        {{env!r}}
        import mlflow{impl}    c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """
        print(f"{sql}")
        return Udf(
            pyexasol_connection, language_alias, db_schema_name, name, sql, env
        ).create()

    return create


def test_bfs_load_model(create_udf, logged_sample_model) -> None:
    """
    Use a sample model already logged to MLflow server and represented by
    its URI as returned by fixture `logged_sample_model`.

    Create a UDF reading the model from BucketFS mounted as path in the local
    file system.
    """

    udf = create_udf(
        "BFS_LOAD_MLFLOW_MODEL",
        """
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
            udf_path
        )
        def run(ctx):
            path = udf_path(ctx.uri)
            model = mlflow.sklearn.load_model(path)
        """,
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == SKLEARN_PACKAGE


def test_http_load_model(
    mlflow_tracking_uri,
    create_udf,
    logged_sample_model: str,
) -> None:
    """
    Use a sample model already logged to MLflow server and represented by
    its URI as returned by fixture `logged_sample_model`.

    Create a UDF reading the model via HTTP to the MLflow server.

    Environment variable ENV_BUCKETFS_PASSWORD is set to "not required" as
    the test uses a public bucket and the UDF performs only read-operations.

    Note: Private buckets can be read using the read-password as well as the
    write-password).
    """

    udf = create_udf(
        "HTTP_LOAD_MLFLOW_MODEL",
        """
        def run(ctx):
            model = mlflow.sklearn.load_model(ctx.uri)
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            MLFLOW_TRACKING_URI: mlflow_tracking_uri,
        },
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == SKLEARN_PACKAGE


def test_load_model_with_fallback_1(
    mlflow_tracking_uri, create_udf, non_bucketfs_model: str
) -> None:
    """
    Given a model, with an experiment not using BucketFS as artifact
    store: Try to load the model from BucketFS mounted into local file system.

    Expect the model to be loaded successfully, though, by utilizing the
    fallback loading the model by its URI via network data transfer.
    """

    udf = create_udf(
        "LOAD_MLFLOW_MODEL_WITH_FALLBACK_1",
        """
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
            load_model_with_fallback
        )
        def run(ctx):
            model = load_model_with_fallback(ctx.uri, mlflow.sklearn.load_model)
        """,
        env={"MLFLOW_TRACKING_URI": mlflow_tracking_uri},
    )
    result = udf.run(non_bucketfs_model).fetchone()
    assert result[0] == SKLEARN_PACKAGE


@pytest.fixture
def xnon_bucketfs_model():
    return "mlflow-artifacts:/2/models/m-0b55c1c46bcd47f9a633bc3fd1b59e4a/artifacts"


def test_load_model_with_fallback_2(
    mlflow_tracking_uri, create_udf, non_bucketfs_model: str
) -> None:
    """
    Given a model, with an experiment not using BucketFS as artifact
    store: Try to load the model from BucketFS mounted into local file system.

    Expect the model to be loaded successfully, though, by utilizing the
    fallback loading the model by its URI via network data transfer.
    """

    udf = create_udf(
        "LOAD_MLFLOW_MODEL_WITH_FALLBACK_2",
        """
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
            local_path_or_uri
        )
        def run(ctx):
            locator = local_path_or_uri(ctx.uri)
            model = mlflow.sklearn.load_model(locator)
        """,
        env={"MLFLOW_TRACKING_URI": mlflow_tracking_uri},
    )
    result = udf.run(non_bucketfs_model).fetchone()
    assert result[0] == SKLEARN_PACKAGE
