from typing import Any

from exasol.mlflow_plugin.rest_api.column import Column

JsonObject = dict[str, Any]

__all__ = [
    "Column",
    "JsonObject",
]
