import exasol.bucketfs as bfs
import pytest
from mlflow.entities import FileInfo

# This import is required to avoid warnings about circular import of
# BucketFsArtifactRepo
from mlflow.store.artifact.artifact_repo import ArtifactRepository as _

from exasol.mlflow_plugin.artifacts.repo import BucketFsArtifactRepo

SAMPLE_FILES = {"file-1.txt", "dir/file-2.txt", "dir/file-3.txt"}


@pytest.fixture
def testee(connector) -> BucketFsArtifactRepo:
    return BucketFsArtifactRepo(connector.uri)


def filenames(bfsloc: bfs.path.PathLike) -> list[str]:
    result = []
    for root, _, files in bfsloc.walk():
        result += [str(root/f) for f in files]
    return set(result)


@pytest.mark.dependency()
def test_log_single_artifact(tmp_path, connector, testee) -> None:
    file = tmp_path / "file-2.txt"
    file.write_text(file.name)
    testee.log_artifact(file, "dir")
    expected = connector.bucketfs_location / "dir" / file.name
    assert expected.exists()


@pytest.mark.dependency("test_log_single_artifact")
def test_log_multiple_artifacts(tmp_path, connector, testee) -> None:
    """
    This test is also marked as dependency to other tests for listing and
    downloading artifacts.
    """

    for f in SAMPLE_FILES:
        path = tmp_path / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f)

    testee.log_artifacts(tmp_path)
    actual = filenames(connector.bucketfs_location)
    assert actual == set(SAMPLE_FILES)


@pytest.mark.dependency(depends=["test_log_multiple_artifacts"])
def test_list(testee) -> None:
    actual = testee.list_artifacts()
    assert all(isinstance(f, FileInfo) for f in actual)
    assert {f.path for f in actual} == SAMPLE_FILES


@pytest.mark.dependency(depends=["test_log_multiple_artifacts"])
def test_download(tmp_path, testee) -> None:
    testee.download_artifacts(".", tmp_path)
    actual = {str(f.relative_to(tmp_path)) for f in tmp_path.glob("**/*.*")}
    assert actual == SAMPLE_FILES
