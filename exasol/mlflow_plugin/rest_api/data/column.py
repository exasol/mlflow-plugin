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
        header: str = "",
        data_type: str = "",
        align: str = "left",
        key: str = "",
    ):
        self.name = name
        self.key = key or name
        self.header = header or name.title().replace("_", " ")
        self.width = width
        self.data_type = data_type
        self.align = align

    def process(self, value: Any) -> Any:
        return value if self.data_type != "timestamp" else time_str(value)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Column)
            and other.name == self.name
            and other.key == self.key
            and other.width == self.width
            and other.header == self.header
            and other.data_type == self.data_type
            and other.align == self.align
        )

    @classmethod
    def timestamp(cls, name: str, header: str) -> Column:
        return cls(name, 20, header=header, data_type="timestamp")
