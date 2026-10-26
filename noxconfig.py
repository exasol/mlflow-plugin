from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig

PROJECT_CONFIG = BaseConfig(
    project_name="mlflow_plugin",
    root_path=Path(__file__).parent,
    # pytest-exasol-backend requires Python <3.14
    python_versions=("3.11", "3.13"),
    minimum_python_version="3.11",
    exasol_versions=("2025.1.8",),
)
