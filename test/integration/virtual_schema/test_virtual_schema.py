import importlib.resources

from exasol.pytest_slc import udf_debug
from exasol.pytest_slc.udf_debug.udf_output_logger import alter_session_sql

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
    vs.drop(con)
    pipe = udf_debug.LogPipe()
    expected = ["Adapter call: createVirtualSchema", "Adapter call: dropVirtualSchema"]
    with udf_debug.UdfOutputLogger(query=con.execute, print_func=pipe.input):
        vs.create(con)
        # The adapter <A> is created in DB schema db_schema_name <S>.
        #
        # The VS schema needs to be dropped before fixture pyexasol_connection
        # from pytest-extension drops the <S> when the test session has
        # finished to avoid the following error
        #
        # The schema <S>_name contains the Adapter Script <A> for which
        # at least one Virtual Schema exists (MLFLOW_VS).  Please drop all
        # Virtual Schemas of this Adapter first.
        vs.drop(con)
        udf_debug.wait_for_messages(pipe.output, *expected)
    # see https://github.com/exasol/pytest-slc/issues/41
    con.execute(alter_session_sql(""))
