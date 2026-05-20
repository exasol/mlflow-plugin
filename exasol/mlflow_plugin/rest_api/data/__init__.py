from typing import Any

from exasol.mlflow_plugin.rest_api.data.column import Column

JsonObject = dict[str, Any]

__all__ = [
    "Column",
    "JsonObject",
]
