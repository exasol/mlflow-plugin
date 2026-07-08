from __future__ import annotations

from datetime import (
    datetime,
)
from typing import Any

JsonObject = dict[str, Any]


def timestamp_to_datetime(seconds_since_epoc: int) -> datetime:
    """
    Convert MLflow timestamp to datetime.

    Please note: The MLflow REST API returns timestamps as INT64, representing
    milliseconds since the UNIX, see
    https://mlflow.org/docs/latest/api_reference/rest-api.html

    UDFs require time zone naive timestamps, i.e. representing a UTC value but
    without explicit time zone annotation, such as suffix "+00:00" or "Z".

    The Unix epoch is defined to use UTC. Still, we omit the timezone info to
    avoid the database to fail with a parsing error on suffix "+00:00".

    Sonar warning python:S6903 is therefore ignored.
    """
    return datetime.utcfromtimestamp(seconds_since_epoc / 1000)  # NOSONAR


SQL_TYPE = {
    bool: "BOOLEAN",
    int: "DECIMAL",
    datetime: "TIMESTAMP",
}


class Column:
    def __init__(
        self,
        name: str,
        size: int,
        sql_name: str = "",
        data_type: type = str,
        key: str = "",
        comma_sep: bool = False,
    ):
        self.name = name
        self.sql_name = sql_name or name
        self.size = size
        self.data_type = data_type
        self.key = key or name
        self.comma_sep = comma_sep

    @property
    def _sql_data_type(self) -> str:
        return SQL_TYPE.get(self.data_type, "VARCHAR")

    @property
    def _json_data_type(self) -> JsonObject:
        def data_type():
            yield "type", self._sql_data_type
            if self.data_type == int:
                yield "precision", self.size
                yield "scale", 0
            if self.data_type == str:
                yield "size", self.size

        return dict(data_type())

    @property
    def json(self) -> JsonObject:
        return {"name": self.sql_name, "dataType": self._json_data_type}

    @property
    def sql_type(self) -> str:
        def suffix() -> str:
            jdt = self._json_data_type
            if size := jdt.get("size"):
                return f"({size})"
            if self.data_type == datetime:
                return "(3)"
            if precision := jdt.get("precision"):
                scale = jdt.get("scale", 0)
                return f"({precision},{scale})"
            return ""

        return f"{self._sql_data_type}{suffix()}"

    @property
    def sql(self) -> str:
        return f'"{self.sql_name}" {self.sql_type}'

    def process(self, value: Any) -> Any:
        if value and self.data_type == datetime:
            return timestamp_to_datetime(value)
        return value

    def __repr__(self) -> str:
        atts = ", ".join(
            f"{x}={str(getattr(self, x))}"
            for x in "name size sql_name data_type key comma_sep".split()
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
    def boolean(cls, name: str, sql_name: str = "") -> Column:
        return cls(name, size=1, sql_name=sql_name, data_type=bool)

    @classmethod
    def timestamp(cls, name: str, sql_name: str = "") -> Column:
        return cls(name, 3, sql_name=sql_name, data_type=datetime)

    @classmethod
    def decimal(
        cls,
        name: str,
        precision: int = 18,
        sql_name: str = "",
        key: str = "",
    ) -> Column:
        return cls(name, size=precision, sql_name=sql_name, data_type=int, key=key)

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
            data_type=str,
            key=key,
            comma_sep=comma_sep,
        )
