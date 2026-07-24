from inspect import cleandoc

ADAPTER_IMPL = cleandoc("""
    from exasol.mlflow_plugin.rest_api.vs_impl import RequestHandler

    HANDLER = RequestHandler(exa.meta)

    def adapter_call(request_str):
        return HANDLER.handle(request_str)
    """)
