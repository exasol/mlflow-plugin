from typing import (
    Any,
    Type,
)


class Body:
    # formerly known as UdfBase
    """
    Adapter from the UDF-specific objects exa and ctx to the Python
    classes accessing the MLflow REST API.

    * Retrieve base URL and credentials from Connection object.
    * Instantiate the specified class for accessing the resp. REST endpoint.
    * Iterate over the rows returned by the endpoint.
    * Pass each row to the UDF context object.
    """
    def __init__(self, exa, api_cls: Type[Any]):
        # typehint could use a list of classes or a common super class.
        """
        mapping: Maps names of UDF args to names of args in endpoint.call()
        """
        self._exa = exa
        self._api_cls = api_cls
        # infos = exa.get_connection()
        # base_url = self.create_url(infos)
        # self.endpoint = api(base_url)

    def run(self, ctx):
        # endpoint = ExperimentsSearch("URI", ("admin", "password1234"))
        # conn.address should contain something like
        # "http://localhost:5000/api/2.0/mlflow"
        conn = self._exa.get_connection(ctx.connection_name)
        endpoint = self._api_cls(conn.address, auth=(conn.user, conn.password))
        params = {n: ctx[n] for n in self._api_cls.param_names}
        for row in endpoint.call(**params):
            ctx.emit(*row)
