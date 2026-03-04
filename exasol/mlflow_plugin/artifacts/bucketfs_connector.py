"""
Parse BucketFS parameters from artifact root string.

Sample exa+bfs://localhost:2580/bfsdefault/default/my_path

The following URL schemes are planned for accessing the BucketFS
provided by various database instances and access protocols:

* exa+bfs: onprem HTTP
* exa+bfss: onprem HTTPS
* exa+saas: SaaS instance
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import exasol.bucketfs as bfs

from exasol.mlflow_plugin.env_vars import (
    ENV_BUCKETFS_PASSWORD,
    ENV_BUCKETFS_USER,
    ENV_SSL_CERT_VALIDATION,
    str_to_bool,
)

URL_SCHEMES = ["exa+bfs", "exa+bfss"]


class BfsSpecError(Exception):
    """
    Insufficient or invalid connection parameters for Exasol
    BucketFS.

    Subclases:
    * ParseError: Required parameters cannot be parsed from the artifact_root
    * EnvError: A required environment variable is not set.
    """


class ParseError(BfsSpecError):
    """
    Failed to parse a fully specified BucketFS location from an
    artifact_root string.
    """


class EnvError(BfsSpecError):
    """
    Required environment variable was not set.
    """


def parse_onprem_url(artifact_root: str) -> tuple[str, str, str, str]:
    url = urlparse(artifact_root)
    if url.scheme not in URL_SCHEMES:
        raise ParseError(
            f'Artifact_root "{artifact_root}" is not in {URL_SCHEMES}.'
            " As this indicates an internal error,"
            " please open an issue at"
            " https://github.com/exasol/mlflow-plugin/issues/new"
        )
    parts = Path(url.path).parts
    if len(parts) < 3:
        raise ParseError(
            f'Artifact_root "{artifact_root}" must contain'
            " BucketFS service name and bucket name."
        )

    parts = Path(url.path).parts
    service = parts[1]
    bucket = parts[2]
    rest = parts[3:]
    path = "/".join(rest) if rest else ""
    protocol = "https" if url.scheme == "exa+bfss" else "http"
    return (f"{protocol}://{url.netloc}", service, bucket, path)


@dataclass(frozen=True)
class Connector:
    """
    Provides parameters for accessing Exasol BucketFS via MLflow artifact
    store or directly.
    """

    uri: str
    username: str
    password: str
    ssl_cert_validation: bool
    verify_bucket: bool = True

    @property
    def bucketfs_parameters(self) -> dict[str, Any]:
        url, service, bucket, path = parse_onprem_url(self.uri)
        return {
            "backend": "onprem",
            "url": url,
            "username": self.username,
            "password": self.password,
            "service_name": service,
            "bucket_name": bucket,
            "verify": self.ssl_cert_validation,
            "path": path,
            "verify_bucket": self.verify_bucket,
        }

    @property
    def bucketfs_location(self) -> bfs.path.PathLike:
        return bfs.path.build_path(**self.bucketfs_parameters)

    @classmethod
    def for_udfs(cls, artifact_uri: str) -> Connector:
        return cls(
            artifact_uri,
            username="",
            password="",
            ssl_cert_validation=False,
            verify_bucket=False,
        )

    @classmethod
    def from_env(cls, artifact_uri: str) -> Connector:
        password = os.getenv(ENV_BUCKETFS_PASSWORD)
        if not password:
            raise EnvError(
                f"Environment variable {ENV_BUCKETFS_PASSWORD} must be"
                " set to the write password for uploading files to the BucketFS."
            )
        bfs_write_user = os.getenv(ENV_BUCKETFS_USER, "w")
        ssl_cert_validation = os.getenv(ENV_SSL_CERT_VALIDATION, "true")
        return cls(
            artifact_uri,
            bfs_write_user,
            password,
            str_to_bool(ssl_cert_validation),
        )


def udf_path(artifact_uri: str) -> str:
    # con = Connector(artifact_uri, "", "", False)
    con = Connector.for_udfs(artifact_uri)
    return con.bucketfs_location.as_udf_path()
