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
from mlflow.exceptions import MlflowException

# Required to avoid warnings about circular import of BucketFsArtifactRepo
from mlflow.store.artifact.artifact_repo import ArtifactRepository as _  # noqa

from exasol.mlflow_plugin.artifacts.repo import BucketFsArtifactRepo

ROOT_FILE = "root-file.txt"
FILE_IN_DIR = "dir/file-in-dir.txt"
SAMPLE_FILES = ["f1.txt", "dir/f1.txt", "dir/f2.txt"]
ARTIFACT_PATH = "aaa"


def pathlike_content(bfsloc: bfs.path.PathLike) -> list[str]:
    """
    Return the content of the specified BucketFS PathLike as a list of
    strings, adding a slash suffix to directories.
    """

    def entry(f: bfs.path.PathLike) -> str:
        rel = f.relative_to(bfsloc)
        return f"{rel}/" if f.is_dir() else str(rel)

    return sorted([entry(f) for f in bfsloc.iterdir()])


def file_info_str(fi: FileInfo) -> str:
    suffix = "/" if fi.is_dir else ""
    return f"{fi.path}{suffix}"


def create_sample_file(root: Path, entry: str, content: str = "") -> Path:
    path = root / entry
    path.parent.mkdir(exist_ok=True)
    path.write_text(content or entry)
    return path


def normalize_artifact_path(entry: str) -> str | None:
    """Name of parent path or None."""
    parent = str(Path(entry).parent)
    return None if parent == "." else parent


@pytest.fixture(scope="module")
def testee(connector) -> BucketFsArtifactRepo:
    return BucketFsArtifactRepo(connector.uri)


@pytest.mark.parametrize("file", [ROOT_FILE, FILE_IN_DIR])
def test_log_single_artifact(testee, connector, tmp_path, file):
    try:
        local = create_sample_file(tmp_path, file)
        testee.log_artifact(local, normalize_artifact_path(file))
        expected = connector.bucketfs_location / file
        assert expected.exists()
    finally:
        expected.rm()


def test_overwrite(testee, connector, tmp_path):
    file = create_sample_file(tmp_path, "dynamic-file.txt", "initial content")
    bfsloc = connector.bucketfs_location / file.name

    def read_from_bfs(file: Path) -> str:
        return bfs.as_string(bfsloc.read())

    try:
        testee.log_artifact(file)
        assert read_from_bfs(file) == "initial content"

        file.write_text("updated")
        testee.log_artifact(file)
        assert read_from_bfs(file) == "updated"
    finally:
        bfsloc.rm()


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


@pytest.mark.parametrize(
    "path",
    [
        None,
        "non-existing-dir",
    ],
)
def test_empty_list(testee, connector, path):
    assert [] == testee.list_artifacts(path)


def test_log_multiple_artifacts_root(logged_files_1, connector):
    actual = pathlike_content(connector.bucketfs_location)
    assert actual == ["dir/", "f1.txt"]


def test_log_multiple_artifacts_with_artifact_path(logged_files, connector):
    actual = pathlike_content(connector.bucketfs_location / ARTIFACT_PATH)
    assert actual == ["dir/", "f1.txt"]


def list_scenario(
    id: str,
    artifact_path: str | None,
    expected: list[str],
    description: str = "",
):
    return pytest.param(artifact_path, expected, id=id)


@pytest.mark.parametrize(
    "artifact_path, expected",
    [
        list_scenario(
            id="root",
            artifact_path=None,
            expected=["aaa/", "dir/", "f1.txt"],
        ),
        list_scenario(
            id="subdir",
            artifact_path="aaa",
            expected=["aaa/dir/", "aaa/f1.txt"],
        ),
    ],
)
def test_list_artifacts(logged_files, testee, artifact_path, expected):
    file_infos = testee.list_artifacts(artifact_path)
    assert all(isinstance(f, FileInfo) for f in file_infos)
    actual = [file_info_str(f) for f in file_infos]
    assert actual == expected


def download_scenario(
    id: str,
    artifact_path: str | None,
    expected_dirs: list[str],
    description: str = "",
):
    return pytest.param(artifact_path, expected_dirs, id=id)


def expected_filenames(
    files: list[str], prefixes: str | None | list[str] = None
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

    return {entry(p, f) for p in prefixes for f in files}


@pytest.mark.parametrize(
    "artifact_path, expected_dirs",
    [
        download_scenario(
            id="root",
            artifact_path="",
            expected_dirs=["", "aaa"],
            description="""When downloading the root directory, then expect
            the files from the subdirectory to be included.""",
        ),
        download_scenario(id="subdir", artifact_path="aaa", expected_dirs=["aaa"]),
    ],
)
def test_download_success(logged_files, testee, tmp_path, artifact_path, expected_dirs):
    testee.download_artifacts(artifact_path, tmp_path)
    actual = {str(f.relative_to(tmp_path)) for f in tmp_path.glob("**/*.*")}
    expected = expected_filenames(SAMPLE_FILES, expected_dirs)
    assert actual == expected


def test_download_non_existing(testee, tmp_path):
    with pytest.raises(MlflowException):
        testee.download_artifacts("non-existing-file.txt", tmp_path)
