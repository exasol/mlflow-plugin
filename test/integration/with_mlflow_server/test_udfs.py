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
    """
    Use a sample model already logged to MLflow server and represented by
    its URI as returned by fixture `logged_sample_model`.

    Create a UDF reading the model from BucketFS mounted as path in the local
    file system.
    """

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
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
        },
    )
    result = udf.run(logged_sample_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


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
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import mlflow
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
          load_model_with_fallback
        )
        def run(ctx):
            model = load_model_with_fallback(ctx.uri, mlflow.sklearn.load_model)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            "MLFLOW_TRACKING_URI": mlflow_tracking_uri,
        },
    )
    result = udf.run(non_bucketfs_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


def xtest_x2(mlflow_tracking_uri, create_udf):
    udf = create_udf(
        "LOAD_MLFLOW_MODEL_WITH_FALLBACK_2",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import os
        def run(ctx):
            return os.environ.get("MLFLOW_TRACKING_URI")
            # return ctx.uri
        /
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            "MLFLOW_TRACKING_URI": mlflow_tracking_uri,
        },
    )
    uri = "mlflow-artifacts:/2/models/m-0b55c1c46bcd47f9a633bc3fd1b59e4a/artifacts"
    result = udf.run(uri).fetchone()
    print(f"{result[0]}")


@pytest.fixture(scope="session")
def xlanguage_alias(build_slc):
    return "MLFLOW"  # if build_slc else "PYTHON3"


def xtest_x3(mlflow_tracking_uri, create_udf):
    udf = create_udf(
        "LOAD_MLFLOW_MODEL_WITH_FALLBACK_2",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import mlflow
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
          local_path_or_uri
        )
        def run(ctx):
            # locator = local_path_or_uri(ctx.uri)
            model = mlflow.sklearn.load_model(ctx.uri)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            "MLFLOW_TRACKING_URI": mlflow_tracking_uri,
        },
    )
    uri = "mlflow-artifacts:/2/models/m-0b55c1c46bcd47f9a633bc3fd1b59e4a/artifacts"
    result = udf.run(uri).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"


def xtest_x4(mlflow_tracking_uri, create_udf):
    udf = create_udf(
        "LOAD_MLFLOW_MODEL_WITH_FALLBACK_2",
        """
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import requests
        def run(ctx):
            resp = requests.get(
                ctx.uri,
                headers={{"User-Agent": "Mozilla/5.0"}},
                timeout=20,
            )
            resp.raise_for_status()
            return resp.text
        /
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            "MLFLOW_TRACKING_URI": mlflow_tracking_uri,
        },
    )
    uri = "mlflow-artifacts:/2/models/m-0b55c1c46bcd47f9a633bc3fd1b59e4a/artifacts"
    result = udf.run(mlflow_tracking_uri).fetchone()
    print(f'{result}')


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
        --/
        CREATE OR REPLACE {language_alias!r}
           SCALAR SCRIPT {schema!q}.{name!q}(uri VARCHAR(2000))
           RETURNS VARCHAR(2000) AS
        {env!r}
        import mlflow
        from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
          local_path_or_uri
        )
        def run(ctx):
            locator = local_path_or_uri(ctx.uri)
            model = mlflow.sklearn.load_model(locator)
            c = type(model)
            return c.__module__ + "." + c.__name__
        /
        """,
        env={
            ENV_BUCKETFS_PASSWORD: "not required",
            "MLFLOW_TRACKING_URI": mlflow_tracking_uri,
        },
    )
    result = udf.run(non_bucketfs_model).fetchone()
    assert result[0] == "sklearn.linear_model._logistic.LogisticRegression"
