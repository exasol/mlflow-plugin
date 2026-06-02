from inspect import cleandoc
from unittest.mock import (
    Mock,
    call,
)

import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.udf.deployment import (
    Deployable,
    deploy_all,
)


@pytest.fixture
def endpoint() -> rest_api.Endpoint:
    return rest_api.Endpoint(
        var_name="EEE",
        method="post",
        url_suffix="e/s",
        output_key="kkk",
        input_columns=[Column.varchar("i1")],
        output_columns=[Column.varchar("o1")],
    )


def test_sql_rendering(endpoint) -> None:
    language_alias = "LLL"
    deployable = Deployable(language_alias, "schema", endpoint)
    name = '"schema"."EEE"'
    expected = cleandoc(f"""
    --/
    CREATE OR REPLACE {language_alias} SCALAR SCRIPT {name} (
      "connection_name" VARCHAR(2000000),
      "i1" VARCHAR(2000000)
    ) EMITS (
      "o1" VARCHAR(2000000)
    ) AS
    from exasol.mlflow_plugin import rest_api

    body = rest_api.UdfBody(exa, endpoint=rest_api.EEE)

    def run(ctx):
        body.run(ctx)
    /
    """)
    assert deployable.sql == expected


def test_deploy_all():
    args = ("AAA", "SSS")
    mock = Mock()
    deploy_all(*args, pyexasol_connection=mock)

    udf = Deployable(*args, rest_api.EXPERIMENTS_SEARCH)
    assert mock.execute.call_args == call(udf.sql)
