import json
from typing import Any

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint
from exasol.mlflow_plugin.rest_api.streaming import DataStream
from exasol.mlflow_plugin.rest_api.udf.verification import verify_udf_parameters


class UdfCall:
    """
    Handles the UDF-specific objects exa and ctx and calls the DataStream
    accessing the MLflow REST API.

    * Retrieve base URL and credentials from Connection object.
    * Instantiate the specified class for accessing the resp. REST endpoint.
    * Iterate over the rows returned by the endpoint.
    * Pass each row to the UDF context object.
    """

    def __init__(self, exa, endpoint: Endpoint):
        """
        mapping: Maps names of UDF args to names of args in endpoint.call()
        """
        verify_udf_parameters(exa.meta, endpoint)
        self._exa = exa
        self.endpoint = endpoint
        self.connection_name = ""
        self.data_stream: DataStream | None = None

    def params(self, ctx) -> dict[str, Any]:
        def convert(column: Column, v: Any) -> Any:
            return v if v is None or not column.comma_sep else v.split(",")

        return {c.name: convert(c, ctx[c.name]) for c in self.endpoint.input_columns}

    def _auth(self, user: str, password: str) -> tuple[str, str]:
        """
        Read the string values of attributes ``user`` and ``password`` of
        an Exasol connection and return the parameters for authenticating
        against the MLflow server.

        Currently only basic authentication is supported -- a tuple of
        strings, containing the username and the password.
        """

        def jloads(value: str) -> JsonObject:
            return json.loads(value) if value else {}

        data = jloads(user) | jloads(password)
        auth_type = data.get("auth-type")
        if auth_type == "basic":
            return (str(data.get("user")), str(data.get("password")))
        raise NotImplementedError(
            f"MLflow auth-type {repr(auth_type)} is not supported, yet."
        )

    def run(self, ctx) -> None:
        if ctx.connection_name != self.connection_name or self.data_stream is None:
            self.connection_name = ctx.connection_name
            conn = self._exa.get_connection(ctx.connection_name)
            auth = self._auth(conn.user, conn.password)
            self.data_stream = DataStream(
                base_uri=conn.address, auth=auth, endpoint=self.endpoint
            )

        params = self.params(ctx)
        for row in self.data_stream.retrieve(params):
            ctx.emit(*row)
