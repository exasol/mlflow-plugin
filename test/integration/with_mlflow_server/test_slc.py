import logging
from inspect import cleandoc

import mlflow
import pyexasol
import pytest
import sklearn

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
from exasol.mlflow_plugin.artifacts.repo import bfs_location

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logging.getLogger("exasol.bucketfs").setLevel(logging.WARNING)


def assert_udf_running(
    conn: pyexasol.ExaConnection,
    language_alias: str,
    schema: str,
) -> None:
    udf_name = 'LOAD_MLFLOW_MODEL'
    create_udf = cleandoc(
        f"""
        --/
        CREATE OR REPLACE {language_alias}
           SCALAR SCRIPT "{schema}"."{udf_name}"()
           RETURNS BOOLEAN AS

        def run(ctx):
            return True

        /
        """
    )
    conn.execute(create_udf)
    result = conn.execute(f'SELECT "{schema}"."{udf_name}"()').fetchall()
    assert result[0][0] is True


def test_something_with_slc(
    deployed_slc: str,
    language_alias,
    pyexasol_connection: pyexasol.ExaConnection,
    db_schema_name: str,
):
    # create UDF
    # run UDF
    assert_udf_running(
        pyexasol_connection,
        language_alias,
        db_schema_name,
    )


@pytest.fixture
def connector_for_bfs_access(logged_sample_model):
    return Connector(
        logged_sample_model,
        username="not required",
        password="not required",
        ssl_cert_validation=False,
    )


def test_load_model_from_bucketfs(connector_for_bfs_access) -> None:
    path = connector_for_bfs_access.bucketfs_location.as_udf_path()
    print(f'BucketFS Path: {path}')
    return
    loaded = mlflow.sklearn.load_model(path)


def test_load_model_via_http(bucketfs_env_variables, logged_sample_model) -> None:
    # This access method may need environment variables
    # such as BFS user (password not required) and SSL verification.
    loaded = mlflow.sklearn.load_model(logged_sample_model)
    cls = type(loaded)
    fqn = f"{cls.__module__}.{cls.__name__}"
