from mlflow.store.artifact.artifact_repo import ArtifactRepository


class BucketFsArtifactRepo(ArtifactRepository):
    """Custom artifact repository for scheme 'bfs://'"""

    def __init__(
        self,
        artifact_uri: str,
        tracking_uri: str | None = None,
        registry_uri: str | None = None,
    ) -> None:
        # Initialize your artifact storage backend
        super().__init__(artifact_uri)
        print(f"BucketFsArtifactRepo.__init__(artifact_uri={artifact_uri})")

    def log_artifact(self, local_file, artifact_path=None):
        # Upload file to your storage system
        print(
            f"BucketFsArtifactRepo.log_artifact(local_file={local_file}, artifact_path={artifact_path})"
        )

    def log_artifacts(self, local_dir, artifact_path=None):
        print(
            "BucketFsArtifactRepo.log_artifacts("
            f"local_dir={local_dir}, artifact_path={artifact_path})"
        )
        import subprocess  # nosec: B404

        subprocess.run(["ls", "-l", local_dir])  # nosec: B603, B607
        # Upload directory to your storage system

    def list_artifacts(self, path=None):
        # List artifacts in your storage system
        print(f"BucketFsArtifactRepo.list_artifacts(path={path})")

    def download_artifacts(self, artifact_path, dst_path=None):
        # Download artifacts from your storage system
        print(
            f"BucketFsArtifactRepo.download_artifacts(artifact_path={artifact_path}, dst_path={dst_path})"
        )
