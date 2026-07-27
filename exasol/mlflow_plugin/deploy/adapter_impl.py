from inspect import cleandoc

from exasol.mlflow_plugin.deploy.virtual_schema.adapter import Adapter

ADAPTER_NAME = "MLFLOW_VIRTUAL_SCHEMA_ADAPTER"

ADAPTER_IMPL = cleandoc("""
    from exasol.mlflow_plugin.rest_api.vs_impl import RequestHandler

    HANDLER = RequestHandler(exa.meta)

    def adapter_call(request_str):
        return HANDLER.handle(request_str)
    """)


def create_adapter(schema: str, language_alias: str) -> Adapter:
    return Adapter(
        schema=schema,
        name=ADAPTER_NAME,
        impl=ADAPTER_IMPL,
        language_alias=language_alias,
    )
