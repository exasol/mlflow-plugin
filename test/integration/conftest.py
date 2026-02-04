import os
from collections.abc import Generator
from typing import Any
from unittest import mock
from urllib.parse import (
    urlparse,
    urlunparse,
)

import pytest

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
from exasol.mlflow_plugin.env_vars import ENV_BUCKETFS_PASSWORD
from exasol.mlflow_plugin.slc import slc_build_context


class DotAccess:
    def __init__(self, content: dict[str, Any]):
        self._data = content

    def __getattr__(self, key: str):
        return self._data.get(key, "")


def replace_scheme(url: str) -> str:
    parsed = urlparse(url)
    scheme = "exa+bfs" if parsed[0] == "http" else "exa+bfss"
    return urlunparse((scheme,) + parsed[1:])


@pytest.fixture(scope="module")
def connector(backend_aware_bucketfs_params) -> Generator[Connector, None, None]:
    p = DotAccess(backend_aware_bucketfs_params)
    if p.backend == "saas":
        scheme = "exa+saas"
        raise NotImplementedError(f"Backend {p.backend}")

    env = {ENV_BUCKETFS_PASSWORD: p.password}
    with mock.patch.dict(os.environ, env):
        prefix = replace_scheme(p.url)
        uri = f"{prefix}/{p.service_name}/{p.bucket_name}/{p.path}"
        yield Connector(uri, p.username, p.password, p.verify)


class BucketFsCleaner:
    def __init__(self, connector: Connector):
        self._connector = connector

    def rm(self, files: set[str]):
        bfsloc = self._connector.bucketfs_location
        for f in files:
            (bfsloc / f).rm()


@pytest.fixture(scope="module")
def cleaner(connector) -> BucketFsCleaner:
    return BucketFsCleaner(connector)


@pytest.fixture(scope="session")
def language_alias():
    return "MLFLOW"


@pytest.fixture(scope="session")
def slc_builder(use_onprem, use_saas):
    if use_onprem or use_saas:
        with slc_build_context() as builder:
            yield builder
    else:
        yield None
