"""
Parse BucketFS parameters from artifact root string.

Sample bfs://localhost:2580/bfsdefault/default/my_path

Prefixes:
* bfs: use HTTP
* bfss: Use HTTPS
"""

import os
from pathlib import Path
from urllib.parse import (
    ParseResult,
    urlparse,
)

from exasol.mlflow_plugin import env_vars
from exasol.mlflow_plugin.env_vars import str_to_bool

URL_SCHEMES = ["bfs", "bfss"]


class BfsSpecError(Exception):
    """
    Failed to parse a fully specified BucketFS location from an
    artifact_root string.
    """


def parse_url(artifact_root: str) -> ParseResult:
    url = urlparse(artifact_root)
    if url.scheme not in ["bfs", "bfss"]:
        raise BfsSpecError(f'Artifact_root "{artifact_root}" is not in {URL_SCHEMES}.')
    parts = Path(url.path).parts
    if len(parts) < 3:
        raise BfsSpecError(
            f'Artifact_root "{artifact_root}" must contain'
            " BucketFS service name and bucket name."
        )
    return url


def bucketfs_parameters(artifact_root: str) -> dict[str, str | bool]:
    url = parse_url(artifact_root)
    parts = Path(url.path).parts
    service = parts[1]
    bucket = parts[2]
    rest = parts[3:]
    path = "/".join(rest) if rest else ""
    protocol = "https" if url.scheme == "bfss" else "http"
    bfs_write_user = os.getenv(env_vars.ENV_BUCKETFS_USER, "w")
    password = os.getenv(env_vars.ENV_BUCKETFS_PASSWORD)
    if not password:
        raise BfsSpecError(
            f"Environment variable {env_vars.ENV_BUCKETFS_PASSWORD} must be"
            " set to the write password for uploading files to the BucketFS."
        )
    verify = os.getenv(env_vars.ENV_SSL_CERT_VALIDATION, "true")
    return {
        "backend": "onprem",
        "url": f"{protocol}://{url.netloc}",
        "username": bfs_write_user,
        "password": password,
        "service_name": service,
        "bucket_name": bucket,
        "verify": str_to_bool(verify),
        "path": path,
    }
