from typing import (
    TypeVar,
    cast,
)

from exasol.mlflow_plugin.virtual_schema.errors import PropertiesError
from exasol.mlflow_plugin.virtual_schema.types import PropertiesDict

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
        return cast(T, self.type(value))  # type: ignore

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
            self.type(value)  # type: ignore
        except ValueError:
            raise error


class PropertyValidator:
    def __init__(self, properties: list[Property] | None = None):
        self.properties = {p.name: p for p in properties or []}

    def validate(self, values: PropertiesDict, check_mandatory: bool = False) -> None:
        """Values passed by API are always upper case."""

        def error(
            elements: list[str],
            message: str,
            singular: str = "property",
            plural: str = "properties",
        ) -> PropertiesError:
            n = len(elements)
            label = singular if n == 1 else plural
            formatted = message.format(n=n, label=label, elements=", ".join(elements))
            return PropertiesError(formatted)

        if illegal := [k for k in values if k not in self.properties]:
            raise error(illegal, "{n} unsupported {label}: {elements}.")
        if check_mandatory:
            required = [p.name for p in self.properties.values() if p.mandatory]
            if missing := [p for p in required if p not in values]:
                raise error(
                    missing,
                    "{n} mandatory {label} missing: {elements}.",
                    "property is",
                    "properties are",
                )

        for k, v in values.items():
            self.properties[k].validate(v)
