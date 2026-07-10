from dataclasses import dataclass
from inspect import cleandoc

import pyexasol


@dataclass
class Adapter:
    schema: str
    name: str
    impl: str
    language_alias: str = "PYTHON3"

    @property
    def quoted(self) -> str:
        return f'"{self.schema}"."{self.name}"'

    @property
    def sql(self) -> str:
        return cleandoc("""
        --/
        CREATE OR REPLACE {language_alias} ADAPTER SCRIPT {fqn} AS
        {impl}
        /
        """).format(
            language_alias=self.language_alias,
            fqn=self.quoted,
            impl=self.impl.strip(),
        )

    def create(self, con: pyexasol.ExaConnection):
        con.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
        con.execute(self.sql)


@dataclass
class VirtualSchema:
    name: str
    adapter: Adapter

    def drop(self, con: pyexasol.ExaConnection) -> pyexasol.ExaStatement:
        return con.execute(f'DROP VIRTUAL SCHEMA IF EXISTS "{self.name}" CASCADE')

    def create(self, con: pyexasol.ExaConnection) -> pyexasol.ExaStatement:
        self.adapter.create(con)
        return con.execute(
            f'CREATE VIRTUAL SCHEMA "{self.name}"' f" USING {self.adapter.quoted}"
        )
