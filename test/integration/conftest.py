import os
import re

import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD


@pytest.fixture(scope="session")
def backend_aware_bucketfs_params():
    password = os.getenv("BUCKETFS_PASSWORD")
    return {
        "backend": "onprem",
        "url": "http://localhost:2580",
        "username": "w",
        "password": password,
        "service_name": "bfsdefault",
        "bucket_name": "default",
        "verify": False,
        "path": "",
    }


class DotAccess:
    def __init__(self, content):
        self._data = content

    def __getattr__(self, key):
        return self._data[key]


@pytest.fixture # (scope="session")
def connector(monkeypatch, backend_aware_bucketfs_params) -> Connector:
    p = DotAccess(backend_aware_bucketfs_params)
    if p.backend == "saas":
        scheme = "exa+saas"
        raise NotImplementedError(f"Backend {p.backend}")

    monkeypatch.setitem(os.environ, ENV_BUCKETFS_PASSWORD, p.password)
    prefix = re.sub(r"^http(s?)://", "exa+bfs\\1://", p.url)
    uri = f"{prefix}/{p.service_name}/{p.bucket_name}/{p.path}"
    return Connector(uri, p.username, p.password, p.verify)
