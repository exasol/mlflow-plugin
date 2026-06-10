from test.integration.with_mlflow_server.mlflow_connection import MLflowConnection

import requests

from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.rest_api import RestApiError


class GatewayRestApi:
    def __init__(self, mlflow_connection: MLflowConnection):
        self._conn = mlflow_connection

    def call(self, endpoint: str, query: JsonObject) -> JsonObject:
        resp = requests.post(
            f"{self._conn.url}/api/3.0/mlflow/gateway/{endpoint}",
            json=query,
            auth=self._conn.auth,
        )
        if resp.status_code != 200:
            raise RestApiError("post", endpoint, query, resp)
        return resp.json()

    def create_secret(self, name: str) -> str:
        """Create a secret and return its ID"""
        # return "s-fd8f120275a14fd497741e02fb96e74e"
        resp = self.call(
            "secrets/create",
            {
                "secret_name": name,
                "secret_value": [],
                "provider": "",
                "created_by": "",
            },
        )
        return resp["secret"]["secret_id"]

    def create_model_definition(self, secret_id: str, name: str) -> str:
        """Create a model definition and return its ID"""
        # return "d-72a2e09360e74691afdef39f02e2a69a"
        resp = self.call(
            "model-definitions/create",
            {
                "name": name,
                "secret_id": secret_id,
                "provider": "ollama",
                "model_name": "bj1",
                "created_by": "user",
            },
        )
        return resp["model_definition"]["model_definition_id"]

    def create_endpoint(self, model_id: str, name: str) -> None:
        # return
        self.call(
            "endpoints/create",
            {
                "name": name,
                "model_configs": [
                    {
                        "model_definition_id": model_id,
                        "linkage_type": "PRIMARY",
                        "weight": 0.0,
                        "fallback_order": None,
                    },
                ],
            },
        )
