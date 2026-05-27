import datetime

from exasol.mlflow_plugin.rest_api.data import Column


def test_default_values() -> None:
    column = Column("col_suffix", size=20)
    assert column == Column("col_suffix", 20, "col_suffix", "")


def test_timestamp() -> None:
    column = Column.timestamp("col", sql_name="TIME")
    assert column == Column("col", 20, "TIME", "timestamp")
    expected = datetime.datetime.fromisoformat("2026-05-20 08:32:18")
    assert column.process(1779258738 * 1000) == expected
