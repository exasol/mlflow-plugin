from __future__ import annotations

import datetime
from datetime import timezone
from typing import Any


def timestamp_to_datetime(seconds_since_epoc: int) -> datetime.datetime:
    """
    Convert MLflow timestamp to datetime.
    """
    return datetime.datetime.fromtimestamp(seconds_since_epoc / 1000)


SQL_TYPE = {
    "int": "DECIMAL",
    "timestamp": "TIMESTAMP",
}


class Column:
    def __init__(
        self,
        name: str,
        size: int,
        sql_name: str = "",
        data_type: str = "",
        key: str = "",
    ):
        self.name = name
        self.sql_name = sql_name or name # name.upper()
        self.size = size
        self.data_type = data_type or "str"
        self.key = key or name

    @property
    def sql(self) -> str:
        type = SQL_TYPE.get(self.data_type, "VARCHAR")
        size_suffix = f'({self.size})' if self.data_type == "str" else ""
        return f'"{self.sql_name}" {type}{size_suffix}'

    def process(self, value: Any) -> Any:
        return value if self.data_type != "timestamp" else timestamp_to_datetime(value)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Column)
            and other.name == self.name
            and other.sql_name == self.sql_name
            and other.size == self.size
            and other.data_type == self.data_type
            and other.key == self.key
        )

    @classmethod
    def timestamp(cls, name: str, sql_name: str) -> Column:
        return cls(name, 20, sql_name=sql_name, data_type="timestamp")

    @classmethod
    def varchar(
        cls,
        name: str,
        size: int = 2000000,
        sql_name: str = "",
        key: str = "",
    ) -> Column:
        return cls(name, size=size, sql_name=sql_name, data_type="str", key=key)

    @classmethod
    def decimal(cls, name: str, precision: int = 18, sql_name: str = "") -> Column:
        return cls(name, size=precision, sql_name=sql_name, data_type="int")
