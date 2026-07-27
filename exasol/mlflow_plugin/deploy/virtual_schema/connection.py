from dataclasses import dataclass
from inspect import cleandoc

import pyexasol


@dataclass(frozen=True)
class MLflowConnection:
    url: str
    user: str
    password: str

    @property
    def auth(self) -> tuple[str, str]:
        return (self.user, self.password)


@dataclass
class ExasolConnectionObject:
    name: str
    mlflow_connection: MLflowConnection

    @property
    def sql(self) -> str:
        mc = self.mlflow_connection
        return cleandoc(f"""
        CREATE OR REPLACE CONNECTION "{self.name}"
            TO '{mc.url}'
            USER '{{"auth-type": "basic", "user": "{mc.user}"}}'
            IDENTIFIED BY '{{"password": "{mc.password}"}}'
        """)

    def create(self, con: pyexasol.ExaConnection) -> pyexasol.ExaStatement:
        return con.execute(self.sql)
