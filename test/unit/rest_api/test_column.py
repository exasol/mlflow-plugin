import datetime

from exasol.mlflow_plugin.rest_api.data import Column


def test_default_values() -> None:
    column = Column("col", size=20)
    assert column == Column(
        "col", 20, sql_name="col", data_type="str", key="col", comma_sep=False
    )


def test_timestamp() -> None:
    column = Column.timestamp("col", sql_name="TIME")
    assert column == Column("col", 3, "TIME", "timestamp")
    expected = datetime.datetime.fromisoformat("2026-05-20 08:32:18")
    assert column.process(expected.timestamp() * 1000) == expected
    assert column.sql == '"TIME" TIMESTAMP(3)'


def test_varchar() -> None:
    column = Column.varchar("col", sql_name="VVV")
    assert column == Column("col", 2000000, "VVV", "str")
    assert column.sql == '"VVV" VARCHAR(2000000)'


def test_decimal() -> None:
    column = Column.decimal("col", precision=12, sql_name="DDD")
    assert column == Column("col", 12, "DDD", data_type="int")
    assert column.sql == '"DDD" DECIMAL(12,0)'
