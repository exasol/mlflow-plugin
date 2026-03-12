import itertools
import os
from typing import Any
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin.artifacts import bucketfs_connector
from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
    Connector,
    EnvError,
    ParseError,
    load_model_with_fallback,
    local_path_or_uri,
    udf_path,
)
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD

import pytest

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
    monkeypatch.delitem(os.environ, ENV_BUCKETFS_PASSWORD, raising=False)


VALID_ARTIFACT_ROOT = "exa+bfs://localhost:1234/bfsdefault/default"


def test_missing_password(missing_password_env) -> None:
    with pytest.raises(
        EnvError,
        match=f"Environment variable {ENV_BUCKETFS_PASSWORD} must be set",
    ):
        bucketfs_parameters_from_env(VALID_ARTIFACT_ROOT)


def test_for_udfs(missing_password_env) -> None:
    """
    Although ENV_BUCKETFS_PASSWORD is not set, assert no exception is
    raised and the correct path for use inside a UDF to be returned.
    """
    assert udf_path(VALID_ARTIFACT_ROOT) == "/buckets/bfsdefault/default"


def test_local_path_or_uri__path(mock_path_to_exist):
    actual = local_path_or_uri(VALID_ARTIFACT_ROOT)
    assert actual == "/buckets/bfsdefault/default"


def test_load_model_with_fallback__path(mock_path_to_exist):
    mock = Mock()
    load_model_with_fallback(VALID_ARTIFACT_ROOT, mock)
    assert mock.call_args == call("/buckets/bfsdefault/default")


INVALID_URIS = [
    pytest.param("invalid", id="invalid_uri"),
    pytest.param(
        "mlflow-artifacts:/2/models/m-0abc/artifacts", id="non_bfs_uri"
    ),
    pytest.param(VALID_ARTIFACT_ROOT, id="local_path_does_not_exist"),
]


@pytest.mark.parametrize("uri", INVALID_URIS)
def test_local_path_or_uri__uri(uri):
    """
    When uri is VALID_ARTIFACT_ROOT, then still the associated path in the
    local file system does not exist, hence local_path_or_uri() will return
    the original uri.
    """
    assert local_path_or_uri(uri) == uri


@pytest.mark.parametrize("uri", INVALID_URIS)
def test_load_model_with_fallback__uri(uri):
    mock = Mock()
    load_model_with_fallback(uri, mock)
    assert mock.call_args == call(uri)


@pytest.fixture
def mock_path_to_exist(monkeypatch):
    """ Actually mock any path to be rated as existing. """
    mock = Mock()
    mock.exists.return_value = True
    mock.parts = ["/", "bfsdefault", "default"]
    monkeypatch.setattr(bucketfs_connector, "Path", Mock(return_value=mock))
