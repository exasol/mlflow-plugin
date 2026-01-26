"""
Integration tests for BucketFsArtifactRepo in isolation, i.e. without
starting an MLflow server process.

Please note: After deleting a file from BucketFS, you can create the same file
only after some grace period.
"""

from pathlib import Path

import exasol.bucketfs as bfs
import pytest
from mlflow.entities import FileInfo

# Required to avoid warnings about circular import of BucketFsArtifactRepo
from mlflow.store.artifact.artifact_repo import ArtifactRepository as _  # noqa

from exasol.mlflow_plugin.artifacts.repo import BucketFsArtifactRepo

SIMPLE_FILE = "simple-file.txt"
FILE_IN_DIR = "dir/file-in-dir.txt"
SAMPLE_FILES = {"f1.txt", "dir/f1.txt", "dir/f2.txt"}
ARTIFACT_PATH = "aaa"


def filenames(bfsloc: bfs.path.PathLike) -> set[str]:
    result = []
    for root, _, files in bfsloc.walk():
        result += [str(root / f) for f in files]
    return set(result)


def create_sample_file(root: Path, entry: str) -> Path:
    path = root / entry
    path.parent.mkdir(exist_ok=True)
    path.write_text(entry)
    return path


def normalize_artifact_path(entry: str) -> str | None:
    """Name of parent path or None."""
    parent = str(Path(entry).parent)
    return None if parent == "." else parent


def expected_filenames(
    files: set[str], prefixes: str | None | list[str] = None
) -> set[str]:
    """
    This function helps specifing a set of files in a single or in
    multiple directories.  `prefixes` is name of a single directory of a list
    of such.  The returned result repeats the list of files for each directory
    in the list of directories.
    """
    if prefixes is None:
        prefixes = ""
    if isinstance(prefixes, str):
        prefixes = [prefixes]

    def entry(prefix: str, name: str):
        return f"{prefix}/{name}" if prefix else name

    return {entry(p, f) for f in files for p in prefixes}


@pytest.fixture(scope="session")
def testee(connector) -> BucketFsArtifactRepo:
    return BucketFsArtifactRepo(connector.uri)


@pytest.mark.parametrize("file", [SIMPLE_FILE, FILE_IN_DIR])
def test_log_single_artifact(testee, connector, tmp_path, file) -> None:
    local = create_sample_file(tmp_path, file)
    testee.log_artifact(local, normalize_artifact_path(file))
    expected = connector.bucketfs_location / file
    assert expected.exists()
    expected.rm()


@pytest.fixture(scope="session")
def logged_files_1(tmp_path_factory, testee):
    path = tmp_path_factory.mktemp("logged_files_1")
    for f in SAMPLE_FILES:
        create_sample_file(path, f)
    testee.log_artifacts(path)


@pytest.fixture(scope="session")
def logged_files_2(tmp_path_factory, testee):
    path = tmp_path_factory.mktemp("logged_files_2")
    for f in SAMPLE_FILES:
        create_sample_file(path, f)
    testee.log_artifacts(path, ARTIFACT_PATH)


@pytest.fixture(scope="session")
def logged_files(logged_files_1, logged_files_2):
    pass


def test_log_multiple_artifacts_root(logged_files_1, connector) -> None:
    actual = filenames(connector.bucketfs_location)
    assert actual == expected_filenames(SAMPLE_FILES)


def test_log_multiple_artifacts_with_artifact_path(logged_files, connector) -> None:
    actual = filenames(connector.bucketfs_location / ARTIFACT_PATH)
    expected = expected_filenames(SAMPLE_FILES, ARTIFACT_PATH)
    assert actual == expected


@pytest.mark.parametrize("path, expected_dirs", [(None, ["", "aaa"]), ("aaa", ["aaa"])])
def test_list(logged_files, testee, path, expected_dirs) -> None:
    """
    When listing the root directory, then expect the files from the
    subdirectory to be included.
    """

    actual = testee.list_artifacts(path)
    assert all(isinstance(f, FileInfo) for f in actual)
    expected = expected_filenames(SAMPLE_FILES, prefixes=expected_dirs)
    assert {f.path for f in actual} == expected


@pytest.mark.parametrize(
    "artifact_path, expected_dirs",
    [
        ("", ["", "aaa"]),
        ("aaa", ["aaa"]),
    ],
)
def test_download(logged_files, testee, tmp_path, artifact_path, expected_dirs) -> None:
    """
    When downloading the root directory, then expect the files from the
    subdirectory to be included.
    """

    testee.download_artifacts(artifact_path, tmp_path)
    actual = {str(f.relative_to(tmp_path)) for f in tmp_path.glob("**/*.*")}
    expected = expected_filenames(SAMPLE_FILES, expected_dirs)
    assert actual == expected
