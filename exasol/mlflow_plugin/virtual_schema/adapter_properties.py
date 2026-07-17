from exasol.mlflow_plugin.virtual_schema.errors import PropertiesError
from exasol.mlflow_plugin.virtual_schema.types import PropertiesDict


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
