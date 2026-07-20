from collections.abc import Iterator
from inspect import cleandoc

import pytest

from exasol.mlflow_plugin.rest_api import vs_impl
from exasol.mlflow_plugin.virtual_schema.deployment import (
    Adapter,
    VirtualSchema,
)


@pytest.fixture(scope="module")
def vs_adapter(db_schema_name, pyexasol_connection, language_alias):
    adapter_impl = cleandoc("""
    from exasol.mlflow_plugin.rest_api.vs_impl import RequestHandler

    HANDLER = RequestHandler(exa.meta)

    def adapter_call(request_str):
        return HANDLER.handle(request_str)
    """)
    return Adapter(
        db_schema_name,
        "VS_ADAPTER",
        adapter_impl,
        language_alias=language_alias,
    )


@pytest.fixture(scope="module")
def virtual_schema(
    request,
    vs_adapter,
    mlflow_exa_connection,
    pyexasol_connection,
) -> Iterator[VirtualSchema]:
    properties = {
        "CONNECTION_NAME": mlflow_exa_connection,
        "MAX_RESULTS": "100",
    }
    virtual_schema = VirtualSchema("MLFLOW_VS", vs_adapter, properties)
    pyexasol_connection.execute("ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS=''")
    try:
        virtual_schema.create(pyexasol_connection, replace=True)
        yield virtual_schema
    finally:
        if not request.config.getoption("--keep-virtual-schema"):
            virtual_schema.drop(pyexasol_connection)


@pytest.mark.parametrize("rewriter", vs_impl.REWRITERS)
def test_virtual_schema(
    rest_api_udfs,
    virtual_schema,
    sample_data,
    pyexasol_connection,
    rewriter,
) -> None:
    sql = f'SELECT * FROM "{virtual_schema.name}"."{rewriter.table_name}"'
    actual = pyexasol_connection.execute(sql).fetchall()
    assert len(actual) > 0
