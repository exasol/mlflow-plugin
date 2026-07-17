from typing import (
    Any,
    TypeVar,
    cast,
)

from exasol.mlflow_plugin.virtual_schema.errors import PropertiesError
from exasol.mlflow_plugin.virtual_schema.types import (
    JsonObject,
    PropertiesDict,
)


def _get(req: JsonObject, default: Any = None, *keys: str) -> Any:
    """
    Return the value addressed by the specified sequence of keys pointing
    into potentially nested dicts. If one of the keys is not contained, then
    return the specified default value.

    Args:

       req: JsonObject to search in

       default: default value to return in case any of the keys is not found

       keys: sequence of keys to look for in potentially nested dict ``req``.
    """

    current: Any = req
    for k in keys:
        if not (current := current.get(k)):
            return default
    return current


class AdapterProperties:
    def __init__(self, names: list[str] | None = None):
        self.names = [n.upper() for n in names or []]

    def validate(self, values: PropertiesDict) -> PropertiesDict:
        """Values passed by API are always upper case."""
        if not (illegal := [k for k in values if k not in self.names]):
            return values
        n = len(illegal)
        properties = "property" if n == 1 else "properties"
        raise PropertiesError(f"{n} unsupported {properties}: {', '.join(illegal)}.")

    def _initial(self, request: JsonObject) -> JsonObject:
        return _get(request, {}, "schemaMetadataInfo", "properties")

    def initial(self, request: JsonObject) -> JsonObject:
        return self.validate(self._initial(request))

    def update(self, request: JsonObject) -> JsonObject:
        updated = _get(request, {}, "properties")
        pivot = self._initial(request) | self.validate(updated)
        return {k: v for k, v in pivot.items() if v is not None}


T = TypeVar("T")


class Property:
    def __init__(self, name: str, type: type[T], mandatory: bool = False):
        self.name = name.upper()
        self.type = type
        self.mandatory = mandatory

    def value(self, value: str | None) -> T | None:
        if value is None:
            return None
        if self.type == bool:
            return cast(T, value.lower() == "true")
        return cast(T, self.type(value)) # type: ignore

    def validate(self, value: str | None):
        error = PropertiesError(
            f'Illegal value "{value}" for Adapter Property "{self.name}".'
        )
        if value is None:
            return
        if self.type == bool:
            if value.lower() in ["true", "false"]:
                return
            raise error
        try:
            self.type(value) # type: ignore
        except ValueError:
            raise error


class PropertyValidator:
    def __init__(self, properties: list[Property] | None = None):
        self.properties = {p.name: p for p in properties or []}

    def validate(self, values: PropertiesDict) -> None:
        """Values passed by API are always upper case."""
        if (illegal := [k for k in values if k not in self.properties]):
            n = len(illegal)
            properties = "property" if n == 1 else "properties"
            raise PropertiesError(f"{n} unsupported {properties}: {', '.join(illegal)}.")
        for k, v in values.items():
            self.properties[k].validate(v)
