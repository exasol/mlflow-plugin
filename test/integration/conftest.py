import os
import re
from typing import Any

import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD


class DotAccess:
    def __init__(self, content: dict[str, Any]):
        self._data = content

    def __getattr__(self, key: str):
        return self._data.get(key, "")


@pytest.fixture
def connector(monkeypatch, backend_aware_bucketfs_params) -> Connector:
    p = DotAccess(backend_aware_bucketfs_params)
    if p.backend == "saas":
        scheme = "exa+saas"
        raise NotImplementedError(f"Backend {p.backend}")

    monkeypatch.setitem(os.environ, ENV_BUCKETFS_PASSWORD, p.password)
    prefix = re.sub(r"^http(s?)://", "exa+bfs\\1://", p.url)
    uri = f"{prefix}/{p.service_name}/{p.bucket_name}/{p.path}"
    return Connector(uri, p.username, p.password, p.verify)
