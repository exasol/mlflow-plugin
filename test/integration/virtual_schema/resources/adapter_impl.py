import json
from typing import (
    Any,
    TypeAlias,
)

JsonObject: TypeAlias = dict[str, Any]


class AdapterException(Exception):
    pass


def dget(req: dict[str, Any], *keys: str, default: Any = None) -> Any:
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
        if properties := dget(req, "schemaMetadataInfo", "properties", default={}):
            print(f"properties: {properties}", flush=True)
        return copy("type") | {"schemaMetadata": {"tables": []}}
    if type == "dropVirtualSchema":
        return copy("type")
    raise AdapterException(f"Unsupported request type {type}.")


def adapter_call(request_str: str) -> str:
    req = json.loads(request_str)
    resp = build_response(req)
    return json.dumps(resp, indent=2)
