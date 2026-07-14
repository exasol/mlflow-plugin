import json
from typing import (
    Any,
    TypeAlias,
)

JsonObject: TypeAlias = dict[str, Any]


class AdapterException(Exception):
    pass


def _get(req: JsonObject, default: Any = None, *keys: str) -> Any:
    current: Any = req
    for k in keys:
        if not (current := current.get(k)):
            return default
    return current


def build_response(req: JsonObject):
    def copy(*keys):
        return {key: req[key] for key in keys if key in req}

    type = req["type"]
    print(f"Adapter call: {type}", flush=True)
    if type == "createVirtualSchema":
        if properties := _get(req, {}, "schemaMetadataInfo", "properties"):
            print(f"properties: {properties}", flush=True)
        return copy("type") | {"schemaMetadata": {"tables": []}}
    if type == "dropVirtualSchema":
        return copy("type")
    raise AdapterException(f"Unsupported request type {type}.")


def adapter_call(request_str: str) -> str:
    req = json.loads(request_str)
    resp = build_response(req)
    return json.dumps(resp, indent=2)
