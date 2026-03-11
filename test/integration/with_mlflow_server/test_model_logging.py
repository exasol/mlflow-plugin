from __future__ import annotations

import exasol.bucketfs as bfs
import mlflow
import pytest
import sklearn  # type: ignore

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector


def filenames(bfsloc: bfs.path.PathLike) -> set[str]:
    return {f.name for f in bfsloc.iterdir()}


def switch_uri(other: Connector, uri: str) -> Connector:
    return Connector(
        uri,
        other.username,
        other.password,
        other.ssl_cert_validation,
    )


@pytest.mark.parametrize(
    "cls, mlflow_package",
    [
        (sklearn.linear_model.LogisticRegression, mlflow.sklearn),
    ],
)
def test_round_trip(cls, mlflow_package, mlflow_server, connector, bfs_experiment):
    """
    Parameters:

    * cls: Model class to instantiate for the round trip
    * mlflow_package: mlflow package to use for logging and loading the model
      instance.

    See `_validate_logged_model_name()` in
    https://github.com/mlflow/mlflow/blob/master/mlflow/utils/validation.py#L686
    for restrictions on model names.
    """

    model_name = f"{cls.__module__}.{cls.__name__}".replace(".", ">")
    info = mlflow_package.log_model(cls(), name=model_name)
    loaded = mlflow_package.load_model(info.model_uri)
    assert type(loaded) == cls


def test_log_model(connector, logged_sample_model):
    other = switch_uri(connector, logged_sample_model)
    expected = {
        "conda.yaml",
        "python_env.yaml",
        "model.pkl",
        "MLmodel",
        "requirements.txt",
    }
    actual = filenames(other.bucketfs_location)
    assert actual == expected


def test_non_bfs_model(connector, non_bucketfs_model):
    loaded = mlflow.sklearn.load_model(non_bucketfs_model)
    assert type(loaded) == sklearn.linear_model.LogisticRegression


def xtest_x1(monkeypatch):
    import os

    monkeypatch.setitem(os.environ, "MLFLOW_TRACKING_URI", "http://localhost:5000")
    uri = "mlflow-artifacts:/2/models/m-0b55c1c46bcd47f9a633bc3fd1b59e4a/artifacts"
    loaded = mlflow.sklearn.load_model(uri)
    assert type(loaded) == sklearn.linear_model.LogisticRegression
