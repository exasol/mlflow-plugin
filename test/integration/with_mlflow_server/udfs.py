from __future__ import annotations

import logging
from inspect import cleandoc
from typing import Any

from pyexasol import (
    ExaConnection,
    ExaFormatter,
    ExaStatement,
)


def _exa_formatter(quote_ident: bool = True) -> ExaFormatter:
    class ConnectionMock:
        options = {"quote_ident": quote_ident}

    return ExaFormatter(ConnectionMock())


LOG = logging.getLogger(__name__)
EnvSpec = dict[str, str] | None
FORMATTER = _exa_formatter(quote_ident=True)


class Udf:
    def __init__(
        self,
        connection: ExaConnection,
        language_alias: str,
        schema: str,
        name: str,
        impl: str,
        env: EnvSpec = None,
    ):
        self.connection = connection
        self.language_alias = language_alias
        self.schema = schema
        self.name = name
        self.impl = impl
        self._env = env or {}
        self._last_result: ExaStatement | None = None

    def create_schema(self) -> Udf:
        sql = "CREATE SCHEMA IF NOT EXISTS {schema!q}"
        params = {"schema": self.schema}
        self._last_result = self.connection.execute(sql, params)
        return self

    def env(self) -> str:
        return "\n".join(f'%env {k}="{v}";' for k, v in self._env.items())

    def create(self) -> Udf:
        self.create_schema()
        sql = cleandoc(self.impl)
        params = {
            "language_alias": self.language_alias,
            "schema": self.schema,
            "name": self.name,
            "env": self.env(),
        }
        LOG.debug("Creating UDF\n%s", FORMATTER.format(sql, **params))
        self._last_result = self.connection.execute(sql, params)
        return self

    def run(self, *args: str) -> ExaStatement:
        def param(n: int, arg: Any):
            type = "r" if isinstance(arg, (int, float)) else "s"
            return f"{{arg{n+1}!{type}}}"

        args_sql = ", ".join(param(n, arg) for n, arg in enumerate(args))
        args_params = {f"arg{n+1}": arg for n, arg in enumerate(args)}
        sql = f"select {{schema!q}}.{{name!q}}({args_sql})"
        params = {
            "schema": self.schema,
            "name": self.name,
        } | args_params
        return self.connection.execute(sql, params)  # .fetchone()
