from contextlib import contextmanager

from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder,
    find_path_backwards,
)

CONTAINER_NAME = "exasol_mlflow_plugin"


@contextmanager
def slc_build_context():
    with LanguageContainerBuilder(CONTAINER_NAME) as builder:
        project_directory = find_path_backwards("pyproject.toml", __file__).parent
        builder.prepare_flavor(project_directory)
        yield builder
