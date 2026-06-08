import os
from collections.abc import Generator
from dataclasses import dataclass
from inspect import cleandoc
from typing import Any
from unittest import mock
from urllib.parse import (
    urlparse,
    urlunparse,
)

import pyexasol
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
def build_slc(use_onprem, use_saas, request) -> bool:
    """See developer guide for details."""
    if request.config.getoption("--skip-slc"):
        return False
    return use_onprem or use_saas


@pytest.fixture(scope="session")
def language_alias(request):
    """See developer guide for details."""
    return request.config.getoption("--language-alias") or "MLFLOW"


@pytest.fixture(scope="session")
def slc_builder(build_slc):
    if not build_slc:
        yield None
        return
    with slc_build_context() as builder:
        yield builder


@pytest.fixture(scope="module")
def mlflow_exa_connection_name() -> str:
    return "MLFLOW"


@dataclass(frozen=True)
class MLflowConnection:
    url: str
    user: str
    password: str


@pytest.fixture(scope="module")
def mlflow_connection(mlflow_tracking_uri) -> MLflowConnection:
    return MLflowConnection(
        url=f"{mlflow_tracking_uri}/api/2.0/mlflow",
        user="admin",
        password="password1234",
    )


@pytest.fixture(scope="module")
def mlflow_exa_connection(
    mlflow_connection: MLflowConnection,
    mlflow_exa_connection_name: str,
    pyexasol_connection: pyexasol.ExaConnection,
) -> str:
    """
    Create an Exasol Connection object containing credentials to access
    MLflow REST API.
    """
    name = mlflow_exa_connection_name

    sql = cleandoc(f"""
        CREATE OR REPLACE CONNECTION "{mlflow_exa_connection_name}"
            TO '{mlflow_connection.url}'
            USER '{{"auth-type": "basic", "user": "{mlflow_connection.user}"}}'
            IDENTIFIED BY '{{"password": "{mlflow_connection.password}"}}'
    """)
    pyexasol_connection.execute(sql)
    return mlflow_exa_connection_name
