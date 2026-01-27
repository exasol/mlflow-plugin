"""
Integration tests for BucketFsArtifactRepo in isolation, i.e. without
starting an MLflow server process.

Please note: After deleting a file from BucketFS, you can create the same file
only after some grace period.
"""

from dataclasses import dataclass
from pathlib import Path

import exasol.bucketfs as bfs
import pytest
from mlflow.entities import FileInfo

# Required to avoid warnings about circular import of BucketFsArtifactRepo
from mlflow.store.artifact.artifact_repo import ArtifactRepository as _  # noqa

from exasol.mlflow_plugin.artifacts.repo import BucketFsArtifactRepo


@pytest.fixture(scope="session")
def backend_aware_bucketfs_params():
    import os

    password = os.getenv("BUCKETFS_PASSWORD")
    return {
        "backend": "onprem",
        "url": "http://localhost:2580",
        "username": "w",
        "password": password,
        "service_name": "bfsdefault",
        "bucket_name": "default",
        "verify": False,
        "path": "",
    }


ROOT_FILE = "root-file.txt"
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


@pytest.fixture(scope="module")
def testee(connector) -> BucketFsArtifactRepo:
    return BucketFsArtifactRepo(connector.uri)


@pytest.mark.parametrize("file", [ROOT_FILE, FILE_IN_DIR])
def test_log_single_artifact(testee, connector, tmp_path, file):
    local = create_sample_file(tmp_path, file)
    testee.log_artifact(local, normalize_artifact_path(file))
    expected = connector.bucketfs_location / file
    assert expected.exists()
    expected.rm()


@pytest.fixture(scope="module")
def logged_files_1(tmp_path_factory, testee, cleaner):
    path = tmp_path_factory.mktemp("logged_files_1")
    for f in SAMPLE_FILES:
        create_sample_file(path, f)
    testee.log_artifacts(path)
    try:
        yield
    finally:
        cleaner.rm(SAMPLE_FILES)


@pytest.fixture(scope="module")
def logged_files(logged_files_1, tmp_path_factory, cleaner, testee):
    path = tmp_path_factory.mktemp("logged_files_2")
    for f in SAMPLE_FILES:
        create_sample_file(path, f)
    testee.log_artifacts(path, ARTIFACT_PATH)
    try:
        yield
    finally:
        cleaner.rm({f"{ARTIFACT_PATH}/{f}" for f in SAMPLE_FILES})


def test_log_multiple_artifacts_root(logged_files_1, connector):
    actual = filenames(connector.bucketfs_location)
    assert actual == expected_filenames(logged_files_1)


def test_log_multiple_artifacts_with_artifact_path(logged_files, connector):
    actual = filenames(connector.bucketfs_location / ARTIFACT_PATH)
    expected = expected_filenames(SAMPLE_FILES, ARTIFACT_PATH)
    assert actual == expected


@dataclass(frozen=True)
class Scenario:
    artifact_path: str | None
    expected_dirs: list[str]

    def expectation(self, files: set[str]) -> set[str]:
        """
        Return the set of expected files, based on the initial set of
        files within the expected directories.
        """
        return expected_filenames(files, self.expected_dirs)


@pytest.mark.parametrize(
    "scenario",
    [
        # When listing the root directory, then expect the files from the
        # subdirectory to be included.
        Scenario(artifact_path=None, expected_dirs=["", "aaa"]),
        Scenario(artifact_path="aaa", expected_dirs=["aaa"]),
    ],
)
def test_list(logged_files, testee, scenario):
    actual = testee.list_artifacts(scenario.artifact_path)
    assert all(isinstance(f, FileInfo) for f in actual)
    assert {f.path for f in actual} == scenario.expectation(SAMPLE_FILES)


@pytest.mark.parametrize(
    "scenario",
    [
        # When downloading the root directory, then expect the files from the
        # subdirectory to be included.
        Scenario(artifact_path="", expected_dirs=["", "aaa"]),
        Scenario(artifact_path="aaa", expected_dirs=["aaa"]),
    ],
)
def test_download(logged_files, testee, tmp_path, scenario):
    testee.download_artifacts(scenario.artifact_path, tmp_path)
    actual = {str(f.relative_to(tmp_path)) for f in tmp_path.glob("**/*.*")}
    assert actual == scenario.expectation(SAMPLE_FILES)
