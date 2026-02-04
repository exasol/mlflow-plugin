import subprocess
from exasol.python_extension_common.deployment.language_container_builder import (
    find_path_backwards,
)

import pytest


@pytest.fixture
def dir_context():
    return find_path_backwards("pyproject.toml", __file__).parent


def test_poetry_version(dir_context) -> None:
    print(f'\ndir_context: {dir_context}')
    subprocess.run(["poetry", "--version"])
    subprocess.run(["poetry", "export", "--without-hashes", "--without-urls"])
