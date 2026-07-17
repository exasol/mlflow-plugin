from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExaMetaColumn:
    name: str
    sql_type: str
    type: type
    length: int
    precision: int
    scale: int

    @classmethod
    def boolean(cls, name: str) -> ExaMetaColumn:
        return cls(name, "BOOLEAN", bool, 0, 0, 0)

    @classmethod
    def timestamp(cls, name: str) -> ExaMetaColumn:
        return cls(name, "TIMESTAMP(3)", datetime, 0, 0, 0)

    @classmethod
    def decimal(cls, name: str, precision: int = 18, scale: int = 0) -> ExaMetaColumn:
        return cls(name, f"DECIMAL({precision},{scale})", int, 0, precision, scale)

    @classmethod
    def varchar(cls, name: str, length: int = 2000000) -> ExaMetaColumn:
        return cls(name, f"VARCHAR({length})", str, length, 0, 0)


@dataclass
class ExaMeta:
    input_columns: list[ExaMetaColumn]
    output_columns: list[ExaMetaColumn]
    script_schema: str
