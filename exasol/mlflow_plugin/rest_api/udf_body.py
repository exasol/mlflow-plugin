from typing import Any

from exasol.mlflow_plugin.rest_api.adapter import ApiAdapter
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.endpoints.endpoint import Endpoint


class UdfBody:
    """
    Adapter from the UDF-specific objects exa and ctx to the Python
    classes accessing the MLflow REST API.

    * Retrieve base URL and credentials from Connection object.
    * Instantiate the specified class for accessing the resp. REST endpoint.
    * Iterate over the rows returned by the endpoint.
    * Pass each row to the UDF context object.
    """

    def __init__(self, exa, endpoint: Endpoint):
        """
        mapping: Maps names of UDF args to names of args in endpoint.call()
        """
        self._exa = exa
        self.endpoint = endpoint
        self.connection_name = ""
        self.adapter: ApiAdapter | None = None

    def params(self, ctx) -> dict[str, Any]:
        def convert(column: Column, v: Any) -> Any:
            return v.split(",") if column.comma_sep else v

        return {c.name: convert(c, ctx[c.name]) for c in self.endpoint.input_columns}

    def run(self, ctx) -> None:
        if ctx.connection_name != self.connection_name or self.adapter is None:
            self.connection_name = ctx.connection_name
            conn = self._exa.get_connection(ctx.connection_name)
            auth = (conn.user, conn.password)
            self.adapter = ApiAdapter(
                base_uri=conn.address, auth=auth, endpoint=self.endpoint
            )

        params = self.params(ctx)
        for row in self.adapter.call(params):
            ctx.emit(*row)
