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
    ):
        self.name = name
        self.header = header or name.title().replace("_", " ")
        self.width = width
        self.data_type = data_type
        self.align = align

    def sql(self, value: Any) -> Any:
        if self.data_type != "timestamp":
            return value
        return time_str(value)

    def format(self, value: Any, body: bool = True) -> str:
        if self.data_type == "timestamp" and body:
            v = time_str(value)
        else:
            v = str(value)
        if body and self.align == "right":
            return v.rjust(self.width)[-self.width :]
        return v.ljust(self.width)[: self.width]

    @classmethod
    def timestamp(cls, name: str, header: str) -> Column:
        return cls(name, 20, header=header, data_type="timestamp")
