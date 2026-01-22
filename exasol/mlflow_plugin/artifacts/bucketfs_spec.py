"""
Parse BucketFS parameters from artifact root string.

Sample exa+bfs://localhost:2580/bfsdefault/default/my_path

The following URL schemes are planned for accessing the BucketFS
provided by various database instances and access protocols:

* exa+bfs: onprem HTTP
* exa+bfss: onprem HTTPS
* exa+saas: SaaS instance
"""

import os
from pathlib import Path
from urllib.parse import urlparse

from exasol.mlflow_plugin.env_vars import (
    ENV_BUCKETFS_PASSWORD,
    ENV_BUCKETFS_USER,
    ENV_SSL_CERT_VALIDATION,
    str_to_bool,
)

URL_SCHEMES = ["exa+bfs", "exa+bfss"]


class BfsSpecError(Exception):
    """
    Failed to parse a fully specified BucketFS location from an
    artifact_root string.
    """


def parse_onprem_url(artifact_root: str) -> tuple[str, str, str, str]:
    url = urlparse(artifact_root)
    if url.scheme not in URL_SCHEMES:
        raise BfsSpecError(
            f'Artifact_root "{artifact_root}" is not in {URL_SCHEMES}.'
            " As this indicates an internal error,"
            " please open an issue at"
            " https://github.com/exasol/mlflow-plugin/issues/new"
        )
    parts = Path(url.path).parts
    if len(parts) < 3:
        raise BfsSpecError(
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


def bucketfs_parameters(artifact_root: str) -> dict[str, str | bool]:
    url, service, bucket, path = parse_onprem_url(artifact_root)
    bfs_write_user = os.getenv(ENV_BUCKETFS_USER, "w")
    password = os.getenv(ENV_BUCKETFS_PASSWORD)
    if not password:
        raise BfsSpecError(
            f"Environment variable {ENV_BUCKETFS_PASSWORD} must be"
            " set to the write password for uploading files to the BucketFS."
        )
    verify = os.getenv(ENV_SSL_CERT_VALIDATION, "true")
    return {
        "backend": "onprem",
        "url": url,
        "username": bfs_write_user,
        "password": password,
        "service_name": service,
        "bucket_name": bucket,
        "verify": str_to_bool(verify),
        "path": path,
    }
