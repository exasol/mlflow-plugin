import importlib.resources

import pytest
from exasol.pytest_slc import udf_debug

from exasol.mlflow_plugin.virtual_schema import (
    Adapter,
    VirtualSchema,
)


@pytest.fixture
def vs_adapter(db_schema_name, pyexasol_connection):
    adapter_impl = (
        importlib.resources.files("test.integration.virtual_schema.resources")
        / "adapter_impl.py"
    ).read_text()
    return Adapter(db_schema_name, "VS_ADAPTER", adapter_impl, language_alias="PYTHON3")


@pytest.fixture
def virtual_schema(vs_adapter, pyexasol_connection):
    properties = {"CONNECTION_NAME": "MLFLOW", "MAX_RESULTS": "100"}
    virtual_schema = VirtualSchema("MLFLOW_VS", vs_adapter, properties)
    pyexasol_connection.execute("ALTER SESSION SET SCRIPT_OUTPUT_ADDRESS=''")
    try:
        yield virtual_schema
    finally:
        # The adapter <A> is created in DB schema db_schema_name <S>.
        #
        # The VS schema needs to be dropped before fixture pyexasol_connection
        # from pytest-extension drops the <S> when the test session has
        # finished to avoid the following error
        #
        # The schema <S>_name contains the Adapter Script <A> for which
        # at least one Virtual Schema exists (MLFLOW_VS).  Please drop all
        # Virtual Schemas of this Adapter first.
        virtual_schema.drop(pyexasol_connection)


def test_adapter(db_schema_name, pyexasol_connection, virtual_schema) -> None:
    def query_func(sql: str) -> udf_debug.QueryResult:
        stmt = pyexasol_connection.execute(sql)
        return [] if stmt.rowcount() == 0 else stmt.fetchall()

    pipe = udf_debug.LogPipe()
    expected = [
        "Adapter call: createVirtualSchema",
        f"properties: {virtual_schema.properties}",
    ]
    with udf_debug.UdfOutputLogger(query=query_func, print_func=pipe.input):
        virtual_schema.create(pyexasol_connection, replace=True)
        udf_debug.wait_for_messages(pipe.output, *expected)
