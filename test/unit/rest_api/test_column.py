from exasol.mlflow_plugin.rest_api.data.column import Column


def test_default_values() -> None:
    column = Column("col_suffix", width=20)
    assert column == Column("col_suffix", 20, "Col Suffix", "", "left")


def test_timestamp() -> None:
    column = Column.timestamp("col", header="Time")
    assert column == Column("col", 20, "Time", "timestamp", "left")
    assert column.process(1779258738 * 1000) == "2026-05-20 06:32:18"
