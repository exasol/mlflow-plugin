--/
CREATE OR REPLACE <LANGUAGE_ALIAS> ADAPTER SCRIPT
  "<ADAPTER_SCHEMA>"."<ADAPTER_NAME>" AS
from exasol.mlflow_plugin.rest_api.vs_impl import RequestHandler

HANDLER = RequestHandler(exa.meta)

def adapter_call(request_str):
    return HANDLER.handle(request_str)
/