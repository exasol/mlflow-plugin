import subprocess


def test_poetry_version() -> None:
    subprocess.run(["poetry", "--version"])
    subprocess.run(["poetry", "export", "--without-hashes", "--without-urls"])
