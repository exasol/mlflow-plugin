from __future__ import annotations

import time
from typing import Any


def time_str(seconds_since_epoc: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds_since_epoc / 1000))


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
        self.data_type = data_type

    def process(self, value: Any) -> Any:
        return value if self.data_type != "timestamp" else time_str(value)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Column)
            and other.name == self.name
            and other.width == self.width
            and other.sql_name == self.sql_name
            and other.data_type == self.data_type
        )

    @classmethod
    def timestamp(cls, name: str, sql_name: str) -> Column:
        return cls(name, 20, sql_name=sql_name, data_type="timestamp")
