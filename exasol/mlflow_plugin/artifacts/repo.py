from __future__ import annotations

import logging
import os
import posixpath
import typing
from pathlib import PurePath

import exasol.bucketfs as bfs
from mlflow.entities import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.utils.file_utils import relative_path_to_artifact_path
from mlflow.utils.uri import validate_path_is_safe

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector


def bfs_location(artifact_uri: str) -> bfs.path.PathLike:
    return Connector.from_env(artifact_uri).bucketfs_location


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def purepath(pathlike: bfs.path.PathLike) -> PurePath:
    """
    BFSPY public interface PathLike currently does not include property
    path, see https://github.com/exasol/bucketfs-python/issues/271.
    """

    if not isinstance(pathlike, bfs._path.BucketPath):
        raise TypeError(f"purepath() does not support instances of {type(pathlike)}.")
    return typing.cast(bfs._path.BucketPath, pathlike).path


class BucketFsArtifactRepo(ArtifactRepository):
    """
    Custom artifact repository for schemes 'exa+bfs://' and 'exa+bfss://'

    The class deliberately uses package 'os' instead of pathlib, for maximum
    compatibility as the plugin is designed for mlflow which also uses package
    'os'.
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
        Upload a single file to BucketFS.

        Calling the method a second time for the same artifact will silently
        overwrite the artifact.

        Sample args:
        * local_file: "/tmp/tmptr2u6e0y/model/requirements.txt"
        * artifact_path: None
        """
        self._log("log_artifact", local_file=local_file, artifact_path=artifact_path)
        artifact_path = artifact_path and validate_path_is_safe(artifact_path)
        parent = self._bfs / artifact_path if artifact_path else self._bfs
        dest = parent / os.path.basename(local_file)
        with open(local_file, "rb") as fd:
            dest.write(fd)

    def _child_path(
        self, root: str, local_dir: str, artifact_path: str | None
    ) -> str | None:
        """
        Compute the artifact_path for files in local_dir wrt. to specified
        root directory and the artifact_path optionally specified for the
        parent directory.
        """
        local_abs = os.path.abspath(local_dir)
        if root == local_abs:
            return artifact_path
        rel_path = os.path.relpath(root, local_abs)
        rel = relative_path_to_artifact_path(rel_path)
        return posixpath.join(artifact_path, rel) if artifact_path else rel

    def log_artifacts(self, local_dir, artifact_path=None):
        """
        Upload all files in the specified local directory to BucketFS.

        Sample args:
        * local_dir: "/tmp/tmptr2u6e0y/model"
        * artifact_path: None
        """
        self._log("log_artifacts", local_dir=local_dir, artifact_path=artifact_path)
        for root, _, files in os.walk(local_dir):
            for f in files:
                path = self._child_path(root, local_dir, artifact_path)
                self.log_artifact(os.path.join(root, f), path)

    def list_artifacts(self, path=None) -> list[FileInfo]:
        """
        List artifacts in BucketFS.

        Sample args:
        * path: "python_env.yaml"

        Please note:

        * Identical to
          mlflow.store.artifact.local_artifact_repo.LocalArtifactRepository
          for non-existing directories this methods does not raise an error,
          but returns an empty list [].

        * BFS does not support empty or pure directories, but only creates
          these on-the-fly when storing a file with a particular parent path.

        * BFS allows files path/F and path/F/file.txt to exist.  In
          consequence a specific path (path/F in this case) can be ambiguous
          and be a file and a directory at the same time.
        """
        self._log("list_artifacts", path=path)
        path = path and validate_path_is_safe(path)

        def info(path: bfs.path.PathLike) -> FileInfo:
            rel = purepath(path).relative_to(purepath(self._bfs))
            LOG.info("- %s", rel)
            return FileInfo(path=str(rel), is_dir=path.is_dir(), file_size=None)

        bfsloc = self._bfs / path if path else self._bfs
        if not bfsloc.is_dir():
            return []
        return sorted(
            [info(path) for path in bfsloc.iterdir()],
            key=lambda fi: fi.path,
        )

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
        remote_file_path = validate_path_is_safe(remote_file_path)
        bfsloc = self._bfs / remote_file_path
        bfs.as_file(bfsloc.read(), local_path)
