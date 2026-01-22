import itertools
import os

import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_spec import (
    BfsSpecError,
    bucketfs_parameters,
)
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD


@pytest.mark.parametrize(
    "artifact_root",
    [
        "x",
        "exa+bfs:",
        "exa+bfss:",
        "bfsx://localhost:1234/bfsdefault/default",
        "exa+bfs://localhost:1234/bfsdefault",
        "exa+bfs://localhost:xxx/bfsdefault/default",
    ],
)
def test_invalid_spec(artifact_root) -> None:
    with pytest.raises(BfsSpecError):
        bucketfs_parameters(artifact_root)


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
    actual = bucketfs_parameters(artifact_root)
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
    }
    assert actual == expected


def test_missing_password() -> None:
    artifact_root = "exa+bfs://localhost:1234/bfsdefault/default"
    with pytest.raises(
        BfsSpecError,
        match=f"Environment variable {ENV_BUCKETFS_PASSWORD} must be set",
    ):
        bucketfs_parameters(artifact_root)
