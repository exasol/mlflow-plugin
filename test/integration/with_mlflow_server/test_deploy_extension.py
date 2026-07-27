import contextlib
import importlib.resources
from collections.abc import Iterable

import pyexasol
import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.deploy import adapter_impl


def _ephemeral(conn: pyexasol.ExaConnection, db_schema: str) -> bool:
    sql = f"SELECT * FROM SYS.EXA_SCHEMAS WHERE SCHEMA_NAME = '{db_schema}'"
    return len(conn.execute(sql).fetchall()) == 0


@pytest.fixture
def open_db_schema(pyexasol_connection):
    con = pyexasol_connection

    @contextlib.contextmanager
    def context(db_schema: str) -> Iterable[str]:
        current = con.execute("SELECT CURRENT_SCHEMA").fetchone()[0]
        ephemeral = _ephemeral(con, db_schema)
        try:
            con.execute(f'CREATE SCHEMA IF NOT EXISTS "{db_schema}"')
            yield db_schema
            if ephemeral:
                con.execute(f'DROP SCHEMA IF EXISTS "{db_schema}" CASCADE')
        finally:
            if current:
                con.execute(f'OPEN SCHEMA "{current}"')

    return context


def test_deploy_extension(
    mlflow_server, deployed_slc, pyexasol_connection, open_db_schema
) -> None:
    sql = (
        importlib.resources.files("exasol.mlflow_plugin.deploy") / "extension.sql"
    ).read_text()
    with open_db_schema("ITEST_DEPLOYMENT") as db_schema:
        pyexasol_connection.execute_sql_script(sql)
        select = (
            "SELECT SCRIPT_NAME FROM EXA_ALL_SCRIPTS"
            f" WHERE SCRIPT_SCHEMA = '{db_schema}'"
        )
        actual = {row[0] for row in pyexasol_connection.execute(select)}

    expected = {e.var_name for e in rest_api.ALL_ENDPOINTS}
    expected.add(adapter_impl.ADAPTER_NAME)
    assert expected == actual
