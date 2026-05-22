from __future__ import annotations

import datetime
from datetime import timezone
from typing import Any


def dtime(seconds_since_epoc: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(seconds_since_epoc / 1000)


SQL_TYPE = {
    "int": "INT",
    "timestamp": "TIMESTAMP",
}


class Column:
    def __init__(
        self,
        name: str,
        width: int,
        sql_name: str = "",
        data_type: str = "",
        key: str = "",
    ):
        self.name = name
        self.sql_name = sql_name or name.upper()
        self.width = width
        self.data_type = data_type or "str"
        self.key = key or name

    @property
    def sql(self) -> str:
        type = SQL_TYPE.get(self.data_type, "VARCHAR")
        return f"{self.sql_name} {type}({self.width})"

    def process(self, value: Any) -> Any:
        return value if self.data_type != "timestamp" else dtime(value)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Column)
            and other.name == self.name
            and other.width == self.width
            and other.sql_name == self.sql_name
            and other.key == self.key
            and other.data_type == self.data_type
            and other.key == self.key
        )

    @classmethod
    def timestamp(cls, name: str, sql_name: str) -> Column:
        return cls(name, 20, sql_name=sql_name, data_type="timestamp")
