from __future__ import annotations

import logging

import exasol.bucketfs as bfs
from mlflow.entities import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector


def bfs_location(artifact_uri: str) -> bfs.path.PathLike:
    return Connector.from_env(artifact_uri).bucketfs_location


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class BucketFsArtifactRepo(ArtifactRepository):
    """
    Custom artifact repository for schemes 'exa+bfs://' and 'exa+bfss://'
    """

    def __init__(
        self,
        artifact_uri: str,
        tracking_uri: str | None = None,
        registry_uri: str | None = None,
    ) -> None:
        """
        Sample args:
        * artifact_uri: "bfs://localhost:2580/bfsdefault/default/my_path/"
                        "0/models/m-e2506c0fa86d43aa8352749b9980c4ec/artifacts"
        """
        super().__init__(artifact_uri)
        self._bfs = bfs_location(artifact_uri)
        self._log("__init__", artifact_uri=artifact_uri)

    def _log(self, file_name: str, **kwargs) -> None:
        def quote(value) -> str:
            return f'"{value}"' if isinstance(value, str) else str(value)

        args = [f"{k}: {quote(v)}" for k, v in kwargs.items()]
        arg_str = ", ".join(args)
        LOG.info("%s.%s(%s)", type(self).__name__, file_name, arg_str)

    def log_artifact(self, local_file, artifact_path=None):
        """
        Upload file to BucketFS

        Sample args:
        * local_file: "/tmp/tmptr2u6e0y/model/requirements.txt"
        * artifact_path: None
        """
        self._log("log_artifact", local_file=local_file, artifact_path=artifact_path)

    def log_artifacts(self, local_dir, artifact_path=None):
        """
        Upload all files in the specified directory to BucketFS

        Sample args:
        * local_dir: "/tmp/tmptr2u6e0y/model"
        * artifact_path: None
        """
        self._log("log_artifacts", local_dir=local_dir, artifact_path=artifact_path)

    def list_artifacts(self, path=None) -> list[FileInfo]:
        """
        List artifacts in BucketFS

        Sample args:
        * path: "python_env.yaml"
        """
        self._log("list_artifacts", path=path)
        return []

    # download_artifacts() is already implemented by class ArtifactRepository,
    # but BucketFsArtifactRepo needs to implement the abstractmethod
    # _download_file().

    def _download_file(self, remote_file_path, local_path):
        """
        Download the specified file from BucketFS to the local filesystem.

        Sample args:
        * remote_file_path: "requirements.txt",
        * local_path: "/tmp/tmp4cdl_a_5/requirements.txt")
        """
        self._log(
            "_download_file",
            remote_file_path=remote_file_path,
            local_path=local_path,
        )
