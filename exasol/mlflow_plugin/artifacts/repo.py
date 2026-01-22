import os
import subprocess
from typing import (
    Any,
    List,
)

import exasol.bucketfs as bfs
from mlflow.store.artifact.artifact_repo import ArtifactRepository

from exasol.mlflow_plugin import connections
from exasol.mlflow_plugin.artifacts.bucketfs_spec import bucketfs_parameters

import logging

def bfs_location(artifact_uri: str) -> bfs.path.PathLike:
    params = bucketfs_parameters(artifact_uri)
    return connections.bucketfs_location(params)


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class BucketFsArtifactRepo(ArtifactRepository):
    """Custom artifact repository for scheme 'bfs://'"""

    def __init__(
        self,
        artifact_uri: str,
        tracking_uri: str | None = None,
        registry_uri: str | None = None,
    ) -> None:
        # Initialize your artifact storage backend
        # artifact_uri=bfs://localhost:2580/bfsdefault/default/my_path/0/models/m-e2506c0fa86d43aa8352749b9980c4ec/artifacts
        super().__init__(artifact_uri)
        # self._bfs = bfs_location(artifact_uri)
        self._log("__init__", artifact_uri=artifact_uri)

    def _log(self, file_name: str, **kwargs) -> None:
        args = [f'{k}: "{v}"' for k, v in kwargs.items()]
        arg_str = ", ".join(args)
        LOG.info("%s.%s(%s)", type(self).__name__, file_name, arg_str)

    def log_artifact(self, local_file, artifact_path=None):
        # Upload file to your storage system
        self._log("log_artifact", local_file=local_file, artifact_path=artifact_path)
        # parent = self._bfs / artifact_path if artifact_path else self._bfs
        # dest = parent / os.path.basename(local_file)
        # with open(local_file, "rb") as fd:
        #     dest.write(fd)

    def log_artifacts(self, local_dir, artifact_path=None):
        self._log("log_artifacts", local_dir=local_dir, artifact_path=artifact_path)
        # import subprocess  # nosec: B404
        # subprocess.run(["ls", "-l", local_dir])  # nosec: B603, B607
        # Upload directory to your storage system

    def list_artifacts(self, path=None):
        # List artifacts in your storage system
        print(f"BucketFsArtifactRepo.list_artifacts(path={path})")

    def download_artifacts(self, artifact_path, dst_path=None):
        # Download artifacts from your storage system
        print(
            "BucketFsArtifactRepo.download_artifacts("
            f"artifact_path={artifact_path}, dst_path={dst_path})"
        )
