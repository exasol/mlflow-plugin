import importlib.resources

from exasol.pytest_slc import udf_debug

from exasol.mlflow_plugin.rest_api.virtual_schema import (
    Adapter,
    VirtualSchema,
)

RESOURCES = importlib.resources.files("test.integration.virtual_schema")


def test_adapter(db_schema_name, pyexasol_connection) -> None:
    con = pyexasol_connection
    adapter_impl = (RESOURCES / "adapter_impl.py").read_text()
    adapter = Adapter(
        db_schema_name, "VS_ADAPTER", adapter_impl, language_alias="PYTHON3"
    )
    vs = VirtualSchema("MLFLOW_VS", adapter)
    pipe = udf_debug.LogPipe()
    expected = ["Adapter call: createVirtualSchema", "Adapter call: dropVirtualSchema"]
    with udf_debug.UdfOutputLogger(query=con.execute, print_func=pipe.input):
        vs.create(con)
        vs.drop(con)
        udf_debug.wait_for_messages(pipe.output, *expected)
