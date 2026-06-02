from __future__ import annotations

import datetime
from typing import Any


def timestamp_to_datetime(seconds_since_epoc: int) -> datetime.datetime:
    """
    Convert MLflow timestamp to datetime.
    """
    return datetime.datetime.fromtimestamp(seconds_since_epoc / 1000)


SQL_TYPE = {
    "bool": "BOOLEAN",
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
        comma_sep: bool = False,
    ):
        self.name = name
        self.sql_name = sql_name or name
        self.size = size
        self.data_type = data_type or "str"
        self.key = key or name
        self.comma_sep = comma_sep

    @property
    def sql_type(self) -> str:
        prefix = SQL_TYPE.get(self.data_type, "VARCHAR")
        if self.data_type in ["str", "timestamp"]:
            suffix = f"({self.size})"
        elif self.data_type == "int":
            suffix = f"({self.size},0)"
        else:
            suffix = ""
        return f"{prefix}{suffix}"

    @property
    def sql(self) -> str:
        return f'"{self.sql_name}" {self.sql_type}'

    def process(self, value: Any) -> Any:
        return value if self.data_type != "timestamp" else timestamp_to_datetime(value)

    def __repr__(self) -> str:
        atts = ", ".join(
            f"{x}={str(getattr(self, x))}"
            for x in "name size sql_name size data_type key comma_sep".split()
        )
        return f"Column({atts})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Column)
            and other.name == self.name
            and other.sql_name == self.sql_name
            and other.size == self.size
            and other.data_type == self.data_type
            and other.key == self.key
            and other.comma_sep == self.comma_sep
        )

    @classmethod
    def timestamp(cls, name: str, sql_name: str = "") -> Column:
        return cls(name, 3, sql_name=sql_name, data_type="timestamp")

    @classmethod
    def decimal(cls, name: str, precision: int = 18, sql_name: str = "") -> Column:
        return cls(name, size=precision, sql_name=sql_name, data_type="int")

    @classmethod
    def boolean(cls, name: str, sql_name: str = "") -> Column:
        return cls(name, size=1, sql_name=sql_name, data_type="bool")

    @classmethod
    def varchar(
        cls,
        name: str,
        size: int = 2000000,
        sql_name: str = "",
        key: str = "",
        comma_sep: bool = False,
    ) -> Column:
        return cls(
            name,
            size=size,
            sql_name=sql_name,
            data_type="str",
            key=key,
            comma_sep=comma_sep,
        )
