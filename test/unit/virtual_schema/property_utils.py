from exasol.mlflow_plugin.virtual_schema import (
    JsonObject,
    PropertiesDict,
)


def property_values(
    initial: PropertiesDict, update: PropertiesDict | None = None
) -> JsonObject:
    return {
        "schemaMetadataInfo": {"properties": initial},
        "properties": update or {},
    }
