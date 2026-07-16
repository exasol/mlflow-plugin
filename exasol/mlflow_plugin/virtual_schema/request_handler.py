import json
from abc import abstractmethod

from exasol.mlflow_plugin.virtual_schema.adapter_properties import AdapterProperties
from exasol.mlflow_plugin.virtual_schema.errors import VirtualSchemaError
from exasol.mlflow_plugin.virtual_schema.types import JsonObject


class RequestHandler:
    """
    Handle requests to a Virtual Schema.
    """

    def __init__(self, properties: AdapterProperties, verbose: bool = False):
        self.properties = properties
        self._verbose = verbose

    @abstractmethod
    def create(self, request: JsonObject) -> JsonObject: ...

    @abstractmethod
    def refresh(self, request: JsonObject) -> JsonObject: ...

    @abstractmethod
    def drop(self, request: JsonObject) -> JsonObject: ...

    @abstractmethod
    def get_capabilities(self, request: JsonObject) -> JsonObject: ...

    @abstractmethod
    def set_properties(self, request: JsonObject) -> JsonObject: ...

    @abstractmethod
    def pushdown(self, request: JsonObject) -> JsonObject: ...

    def build_response(self, request: JsonObject) -> JsonObject:
        _type = request["type"]
        if _type == "createVirtualSchema":
            self.properties.initial(request)
            return self.create(request)
        if _type == "setProperties":
            self.properties.update(request)
            return self.set_properties(request)
        if _type == "refresh":
            return self.refresh(request)
        if _type == "dropVirtualSchema":
            return self.drop(request)
        if _type == "getCapabilities":
            return self.get_capabilities(request)
        if _type == "pushdown":
            return self.pushdown(request)
        raise VirtualSchemaError(f"Unknown request type {_type}")

    def handle(self, request_str: str) -> str:
        def to_str(jsn: JsonObject) -> str:
            return json.dumps(jsn, indent=2)

        request = json.loads(request_str)
        response = self.build_response(request)
        resp_str = to_str(response)
            print(
                f"\nrequest {request['type']}: {to_str(request)}\n"
                f"response: {resp_str}\n",
                flush=True,
            )
        return resp_str
