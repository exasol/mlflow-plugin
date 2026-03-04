import itertools
import os
from typing import Any

import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
    Connector,
    EnvError,
    ParseError,
    udf_path,
)
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD


def bucketfs_parameters_from_env(artifact_root: str) -> dict[str, Any]:
    return Connector.from_env(artifact_root).bucketfs_parameters


@pytest.mark.parametrize(
    "artifact_root",
    [
        "x",
        "exa+bfs:",
        "exa+bfss:",
        "bfsx://localhost:1234/bfsdefault/default",
        "exa+bfs://localhost:1234/bfsdefault",
    ],
)
def test_parse_error(monkeypatch, artifact_root):
    monkeypatch.setitem(os.environ, ENV_BUCKETFS_PASSWORD, "password")
    with pytest.raises(ParseError):
        bucketfs_parameters_from_env(artifact_root)


@pytest.mark.parametrize(
    "protocol, host, port, service, bucket, path",
    itertools.product(
        ["exa+bfs", "exa+bfss"],
        ["localhost", "1.2.3.4"],
        ["1234"],
        ["bfs_service"],
        ["the_bucket"],
        ["", "/path/a"],
    ),
)
def test_valid_spec(monkeypatch, protocol, host, port, service, bucket, path) -> None:
    password = "ppp"
    monkeypatch.setitem(os.environ, ENV_BUCKETFS_PASSWORD, password)
    artifact_root = f"{protocol}://{host}:{port}/{service}/{bucket}{path}"
    actual = bucketfs_parameters_from_env(artifact_root)
    http = "https" if protocol == "exa+bfss" else "http"
    expected = {
        "backend": "onprem",
        "url": f"{http}://{host}:{port}",
        "username": "w",
        "password": password,
        "service_name": service,
        "bucket_name": bucket,
        "verify": True,
        "path": path[1:],
        "verify_bucket": True,
    }
    assert actual == expected


@pytest.fixture
def missing_password_env(monkeypatch) -> None:
    monkeypatch.delitem(os.environ, ENV_BUCKETFS_PASSWORD)


@pytest.fixture
def valid_artifact_root():
    return "exa+bfs://localhost:1234/bfsdefault/default"


def test_missing_password(missing_password_env, valid_artifact_root) -> None:
    with pytest.raises(
        EnvError,
        match=f"Environment variable {ENV_BUCKETFS_PASSWORD} must be set",
    ):
        bucketfs_parameters_from_env(valid_artifact_root)


def test_for_udfs(missing_password_env, valid_artifact_root) -> None:
    """
    Although ENV_BUCKETFS_PASSWORD is not set, assert no exception is
    raised and the correct path for use inside a UDF to be returned.
    """
    assert udf_path(valid_artifact_root) == "/buckets/bfsdefault/default"
